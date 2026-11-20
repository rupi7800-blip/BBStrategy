# Aroon 60 + EMA 90 – backtest sul paniere di BBStrategy

Paniere: `paniere.json` (18 coppie USDT, Binance). Dati: candele spot dal 01/2020 (ogni moneta dalla sua prima quotazione). Timeframe 1d, 4h, 1h.

**Segnale** (a chiusura candela, ingresso all'apertura della successiva):
- long: Aroon(60) rialzista (Up > Down) e prima candela che chiude sopra EMA 90;
- short: Aroon ribassista e prima candela che chiude sotto EMA 90.

**Uscite a confronto**: `ema` (chiusura oltre EMA nel verso opposto), `aroon` (inversione di Aroon), `time` (14 barre).
Costi 0,12% per cambio di posizione (commissione 0,10% + slippage 0,02%, come README Bollinger), una posizione alla volta per moneta. Totale e drawdown sono somme di rendimenti % per operazione (senza capitale né dimensionamento).

Tabella completa (long/short, prima/seconda metà): `risultati_aroon_ema.csv`. Rilancio: `python backtest/aroon_ema.py`.

## Sintesi (long + short, tutto il periodo)

Rapporto = totale % / |drawdown massimo %|, entrambi come somma dei rendimenti per operazione.

| TF | Uscita | N op. | % vincenti | Medio/op. | Totale % | Max DD % | Rapporto | Sharpe |
|---|---|---|---|---|---|---|---|---|
| 1d | ema | 1042 | 25% | +8.36% | 8,716 | -848 | 10.3 | 1.44 |
| 1d | aroon | 490 | 42% | +9.86% | 4,833 | -855 | 5.7 | 1.03 |
| 1d | time | 797 | 50% | +2.21% | 1,763 | -446 | 3.9 | 0.99 |
| 4h | ema | 6900 | 22% | +0.87% | 6,000 | -567 | 10.6 | 1.52 |
| 4h | aroon | 3074 | 38% | +0.63% | 1,923 | -1,067 | 1.8 | 0.67 |
| 4h | time | 5099 | 49% | +0.11% | 572 | -1,182 | 0.5 | 0.36 |
| 1h | ema | 29872 | 19% | -0.03% | -878 | -3,842 | -0.2 | -0.30 |
| 1h | aroon | 12509 | 35% | +0.06% | 714 | -1,794 | 0.4 | 0.27 |
| 1h | time | 21052 | 45% | -0.14% | -3,013 | -3,530 | -0.9 | -2.01 |

## Scelta: 1d, uscita sotto EMA 90, solo long
Miglior rapporto profitto/drawdown di tutte le combinazioni (con il solo lato long): totale 8,678%, drawdown -707%, **rapporto 12.3**, 540 operazioni, medio +16.1%, Sharpe 1.48, t-stat 3.8. Seconda: 4h/ema long+short (10,6). Gli short non aggiungono valore (1d/ema: rapporto 10,3 con short contro 12,3 solo long).
- Stabilità (1d/ema, long+short): rapporto 8,3 nella prima metà del periodo (medio +13,5%), 2,4 nella seconda (medio +3,3%). Dettaglio in `risultati_aroon_ema.csv`.

## Letture
- Il vantaggio è nel lato long sui timeframe lenti; gli short sono nulli o negativi.
- Profilo da trend following: vince circa il 22-25% delle volte, mediana negativa, pochi grandi rialzi.
- Il vantaggio si riduce nella seconda metà del periodo (il rialzo 2020-21 pesa molto), pur restando positivo.
- L'1h non è utilizzabile; l'uscita a tempo è la meno interessante.
- Limiti: totale e drawdown sono somme di rendimenti, non un'equity con capitale; operazioni di monete diverse sovrapposte (t-stat ottimistico); storico non uniforme (ARB, OP, SUI recenti).
