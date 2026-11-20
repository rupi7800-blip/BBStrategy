"""Equity di portafoglio Aroon(60) + EMA(90), solo long, con/senza filtro BTC.

Regole (come aroon_ema.py, solo long):
  ingresso : Aroon rialzista (Up > Down) e prima candela che chiude sopra EMA 90 -> ingresso all'apertura successiva
  uscita   : prima chiusura sotto EMA 90 (e, con filtro, anche quando BTC chiude sotto la propria EMA)
  stop     : stop loss STOP (10%) dal prezzo d'ingresso, valutato dentro la candela (minimo <= livello);
             uscita al livello di stop, o all'apertura se la candela apre gia' sotto. Dopo uno stop si rientra solo
             con un nuovo segnale (prima candela sopra EMA con Aroon rialzista).
  filtro   : BTC chiude sopra la propria EMA (BTC_EMA, default 180 come nel README Bollinger); senza filtro non si apre
Portafoglio: 1/N del capitale per moneta (N = monete del paniere), quota delle monete ferme (o non ancora
quotate) in cassa. Rendimento barra per barra, costo 0,12% per ogni cambio di posizione.
Periodo di misura: dal 2020-11-01 (come README). Selezione = primi 3 anni, verifica = ultimi 3.
Uso: python backtest/aroon_ema_equity.py [cache_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aroon_ema import AROON_N, EMA_N, COST, BARS_PER_YEAR, aroon, fetch, symbols  # noqa: E402

BTC_EMA = 180
STOP = 0.10
START_MEAS = pd.Timestamp("2020-11-01", tz="UTC")
SPLIT = pd.Timestamp("2023-11-01", tz="UTC")


def coin_returns(df, btc_ok, use_filter, stop=None):
    """Serie dei rendimenti per barra di una moneta (0 quando fuori mercato) e numero di operazioni."""
    c, o, lo = df["close"].values, df["open"].values, df["low"].values
    ema = df["close"].ewm(span=EMA_N, adjust=False).mean().values
    up, dn = aroon(df, AROON_N)
    osc = (up - dn).values
    valid = ~np.isnan(osc)
    valid[:EMA_N] = False
    cond = valid & (osc > 0) & (c > ema)
    sig = cond & ~np.r_[False, cond[:-1]]
    ok = btc_ok.reindex(df.index).fillna(False).values if use_filter else np.ones(len(c), bool)
    ret = np.zeros(len(c))
    inpos, trades, n = False, 0, len(c)
    for i in range(n):
        if inpos:
            # barra di ingresso: dall'apertura alla chiusura; poi chiusura su chiusura
            prev = o[i] if entered == i else c[i - 1]
            if entered == i:
                ret[i] -= COST
                entry = o[i]
            lvl = entry * (1 - stop) if stop else None
            if stop and lo[i] <= lvl:
                ret[i] += min(o[i], lvl) / prev - 1 - COST  # stop dentro la candela
                inpos = False
                trades += 1
                continue
            ret[i] += c[i] / prev - 1
            if c[i] < ema[i] or (use_filter and not ok[i]):
                ret[i] -= COST  # uscita alla chiusura di questa barra
                inpos = False
                trades += 1
        elif i + 1 < n and sig[i] and ok[i]:
            inpos, entered = True, i + 1  # entra all'apertura della barra successiva
    if inpos:
        trades += 1
    return pd.Series(ret, index=df.index), trades


def metrics(r, bpy):
    r = r.dropna()
    eq = (1 + r).cumprod()
    yrs = len(r) / bpy
    dd = (eq / eq.cummax() - 1).min()
    sd = r.std(ddof=1)
    tot = eq.iloc[-1] - 1
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if yrs > 0 else np.nan
    return dict(rend_tot=tot * 100, cagr=cagr * 100, maxdd=dd * 100, calmar=(cagr / abs(dd)) if dd < 0 else np.nan,
                sharpe=r.mean() / sd * np.sqrt(bpy) if sd > 0 else np.nan)


def main():
    cache = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if cache:
        import aroon_ema
        aroon_ema.CACHE = cache
    syms = symbols()
    rows = []
    for tf in ["1d", "4h"]:
        bpy = BARS_PER_YEAR[tf]
        data = {s: fetch(s, tf) for s in syms}
        btc = data["BTCUSDT"]["close"]
        btc_ok = btc > btc.ewm(span=BTC_EMA, adjust=False).mean()
        idx = sorted(set().union(*[d.index for d in data.values()]))
        idx = pd.DatetimeIndex(idx)
        idx = idx[idx >= START_MEAS]
        bh = pd.concat({s: d["close"].pct_change() for s, d in data.items()}, axis=1).reindex(idx).fillna(0).sum(axis=1) / len(syms)
        variants = {}
        for name, flt, stp in [("senza filtro, senza stop", False, None), ("con filtro BTC, senza stop", True, None),
                               ("senza filtro, stop 10%", False, STOP), ("con filtro BTC, stop 10%", True, STOP)]:
            rets, ntr, expo = {}, 0, []
            for s, d in data.items():
                r, t = coin_returns(d, btc_ok, flt, stp)
                rets[s] = r.reindex(idx).fillna(0)
                ntr += t
            port = pd.concat(rets, axis=1).sum(axis=1) / len(syms)
            variants[name] = (port, ntr)
        variants["buy&hold 1/N"] = (bh, 0)
        for name, (port, ntr) in variants.items():
            for lab, sl in [("6 anni", slice(None)), ("selezione (3a)", port.index < SPLIT), ("verifica (3a)", port.index >= SPLIT)]:
                p = port[sl] if lab == "6 anni" else port[sl]
                rows.append(dict(tf=tf, variante=name, periodo=lab, operazioni=ntr if lab == "6 anni" else np.nan, **metrics(p, bpy)))
    res = pd.DataFrame(rows)
    out = Path(__file__).resolve().parent / "risultati_aroon_ema_equity.csv"
    res.to_csv(out, index=False)
    pd.set_option("display.width", 200, "display.float_format", lambda v: f"{v:,.2f}")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
