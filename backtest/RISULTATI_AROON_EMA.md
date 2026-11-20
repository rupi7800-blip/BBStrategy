# Aroon 60 + EMA 90 – backtest sul paniere di BBStrategy

Paniere: `paniere.json` (18 coppie USDT, Binance). Dati: candele spot dal 01/2020 (ogni moneta dalla sua prima quotazione). Timeframe 1d, 4h, 1h.

**Segnale** (a chiusura candela, ingresso all'apertura della successiva):
- long: Aroon(60) rialzista (Up > Down) e prima candela che chiude sopra EMA 90;
- short: Aroon ribassista e prima candela che chiude sotto EMA 90.

**Uscite a confronto**: `ema` (chiusura oltre EMA nel verso opposto), `aroon` (inversione di Aroon), `time` (14 barre).
Costi 0,10% per lato (commissione 0,05% + slippage 0,05%), una posizione alla volta per moneta. Totale e drawdown sono somme di rendimenti % per operazione (senza capitale né dimensionamento).

Tabella completa (long/short, prima/seconda metà): `risultati_aroon_ema.csv`. Rilancio: `python backtest/aroon_ema.py`.

## Sintesi (long + short)

| TF | Uscita | N op. | % vincenti | Medio/op. | Mediana | Sharpe | t-stat |
|---|---|---|---|---|---|---|---|
| 1d | ema | 1042 | 25% | +8,40% | -3,58% | 1,45 | 3,7 |
| 1d | aroon | 490 | 42% | +9,90% | -4,62% | 1,03 | 2,7 |
| 1d | time | 797 | 51% | +2,25% | +0,32% | 1,01 | 2,6 |
| 4h | ema | 6900 | 23% | +0,91% | -1,48% | 1,59 | 4,2 |
| 4h | aroon | 3074 | 38% | +0,67% | -1,97% | 0,71 | 1,9 |
| 4h | time | 5099 | 49% | +0,15% | -0,11% | 0,48 | 1,3 |
| 1h | ema | 29872 | 20% | +0,01% | -0,81% | 0,11 | 0,3 |
| 1h | aroon | 12509 | 36% | +0,10% | -1,12% | 0,47 | 1,2 |
| 1h | time | 21052 | 46% | -0,10% | -0,21% | -1,45 | -3,8 |

## Letture
- Il vantaggio è tutto nel **lato long** sui timeframe lenti: 1d/ema long +16,1% a operazione (t 3,8); gli short sono nulli o negativi su ogni timeframe.
- Profilo da trend following: vince 21-25% delle volte, mediana negativa, pochi grandi rialzi.
- Il vantaggio si riduce nel tempo: 1d/ema passa da +13,5% (prima metà) a +3,3% (seconda metà), restando positivo.
- L'1h non è utilizzabile; l'uscita a tempo è la meno interessante.
- Limiti: operazioni di monete diverse sovrapposte (t-stat ottimistico), storico non uniforme (ARB, OP, SUI recenti), costi diversi dal README della strategia Bollinger (0,12% per cambio di posizione).
