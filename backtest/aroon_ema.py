"""Backtest Aroon(60) + EMA(90) sul paniere di BBStrategy (paniere.json, 18 coppie USDT).

Segnale (calcolato a chiusura barra, ingresso all'APERTURA della barra successiva):
  long : Aroon rialzista (AroonUp > AroonDown) e la candela chiude sopra EMA, prima candela che lo fa
         (la barra precedente non soddisfaceva la condizione).
  short: Aroon ribassista (AroonDown > AroonUp) e la candela chiude sotto EMA, prima candela che lo fa.
Uscite a confronto:
  ema   : long chiuso alla prima chiusura sotto EMA (short: sopra EMA)
  aroon : chiusura quando Aroon cambia direzione
  time  : uscita a tempo dopo TIME_BARS barre
Costi: 0,12% per lato (commissione 0,10% + slippage 0,02%). Una posizione alla volta per simbolo.
Uso: python backtest/aroon_ema.py [cache_dir]
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

AROON_N, EMA_N, TIME_BARS = 60, 90, 14
COST = 0.12 / 100  # 0,12% per ogni cambio di posizione (come README Bollinger): commissione 0,10% + slippage 0,02%
START = "2020-01-01"
HOST = "https://data-api.binance.vision/api/v3/klines"
ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "backtest" / "_cache"
BARS_PER_YEAR = {"1d": 365, "4h": 365 * 6, "1h": 365 * 24}


def symbols():
    return json.loads((ROOT / "paniere.json").read_text())["monete"]


def fetch(symbol, interval):
    f = CACHE / f"{symbol}_{interval}.pkl"
    if f.exists():
        return pd.read_pickle(f)
    start = int(pd.Timestamp(START, tz="UTC").timestamp() * 1000)
    rows = []
    while True:
        for attempt in range(5):
            try:
                r = requests.get(HOST, params=dict(symbol=symbol, interval=interval, startTime=start, limit=1000), timeout=30)
                r.raise_for_status()
                break
            except Exception:
                time.sleep(1 + attempt)
        else:
            raise RuntimeError(f"fetch fallito {symbol} {interval}")
        data = r.json()
        if not data:
            break
        rows += data
        start = data[-1][6] + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(rows, columns=range(12))[[0, 1, 2, 3, 4]].astype(float)
    df.columns = ["t", "open", "high", "low", "close"]
    df["t"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    df = df.set_index("t")
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_pickle(f)
    return df


def aroon(df, n):
    w = n + 1
    since_hi = df["high"].rolling(w).apply(lambda x: w - 1 - np.argmax(x), raw=True)
    since_lo = df["low"].rolling(w).apply(lambda x: w - 1 - np.argmin(x), raw=True)
    return 100 * (n - since_hi) / n, 100 * (n - since_lo) / n


def run_symbol(df, exit_mode):
    c, o = df["close"].values, df["open"].values
    ema = df["close"].ewm(span=EMA_N, adjust=False).mean().values
    up, dn = aroon(df, AROON_N)
    osc = (up - dn).values
    valid = ~np.isnan(osc)
    valid[:EMA_N] = False  # warm-up EMA
    long_c = valid & (osc > 0) & (c > ema)
    short_c = valid & (osc < 0) & (c < ema)
    prev_l = np.r_[False, long_c[:-1]]
    prev_s = np.r_[False, short_c[:-1]]
    sig = np.where(long_c & ~prev_l, 1, np.where(short_c & ~prev_s, -1, 0))
    trades = []
    i, n = 0, len(c)
    while i < n - 2:
        d = sig[i]
        if d == 0:
            i += 1
            continue
        e = i + 1
        entry = o[e]
        j = e
        while True:
            j += 1
            if j >= n:
                j = n - 1
                break
            if exit_mode == "ema" and ((d == 1 and c[j] < ema[j]) or (d == -1 and c[j] > ema[j])):
                break
            if exit_mode == "aroon" and valid[j] and ((d == 1 and osc[j] < 0) or (d == -1 and osc[j] > 0)):
                break
            if exit_mode == "time" and j - e >= TIME_BARS:
                break
        # uscita alla chiusura della barra j
        ret = d * (c[j] / entry - 1) - 2 * COST
        trades.append((df.index[e], df.index[j], d, ret, j - e))
        i = j + 1
    return trades


def stats(tr, tf):
    if tr.empty:
        return dict(n=0)
    r = tr["ret"].values
    eq = np.cumsum(r)
    dd = (eq - np.maximum.accumulate(np.r_[0, eq])[1:]).min()
    w, l = r[r > 0], r[r <= 0]
    span_years = (tr["exit"].max() - tr["entry"].min()).days / 365.25
    tpy = len(r) / span_years if span_years > 0 else np.nan
    sd = r.std(ddof=1) if len(r) > 1 else np.nan
    return dict(
        n=len(r), hit=(r > 0).mean() * 100, mean=r.mean() * 100, median=np.median(r) * 100, total=eq[-1] * 100,
        payoff=(w.mean() / -l.mean()) if len(w) and len(l) and l.mean() < 0 else np.nan,
        sharpe=r.mean() / sd * np.sqrt(tpy) if sd and sd > 0 else np.nan,
        maxdd=dd * 100, bars=tr["bars"].mean(),
        t=r.mean() / (sd / np.sqrt(len(r))) if sd and sd > 0 else np.nan,
    )


def main():
    syms = symbols()
    print(f"Paniere ({len(syms)}): {', '.join(syms)}", flush=True)
    out = []
    for tf in ["1d", "4h", "1h"]:
        with ThreadPoolExecutor(6) as ex:
            data = dict(zip(syms, ex.map(lambda s: fetch(s, tf), syms)))
        print(f"[{tf}] dati scaricati: {sum(len(d) for d in data.values())} barre", flush=True)
        for mode in ["ema", "aroon", "time"]:
            rows = []
            for s, df in data.items():
                for e, x, d, r, b in run_symbol(df, mode):
                    rows.append((s, e, x, d, r, b))
            tr = pd.DataFrame(rows, columns=["sym", "entry", "exit", "dir", "ret", "bars"])
            tr = tr.sort_values("entry")
            tr.to_csv(CACHE / f"trades_{tf}_{mode}.csv", index=False)
            half = tr["entry"].quantile(0.5) if len(tr) else None
            for lab, sub in [("tutto", tr), ("long", tr[tr.dir == 1]), ("short", tr[tr.dir == -1]),
                             ("1a meta", tr[tr.entry <= half] if half is not None else tr),
                             ("2a meta", tr[tr.entry > half] if half is not None else tr)]:
                out.append(dict(tf=tf, uscita=mode, sub=lab, **stats(sub, tf)))
    res = pd.DataFrame(out)
    res.to_csv(CACHE / "risultati.csv", index=False)
    pd.set_option("display.width", 220, "display.max_columns", 30, "display.float_format", lambda v: f"{v:,.2f}")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
