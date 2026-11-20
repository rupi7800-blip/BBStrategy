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

## Equity di portafoglio e filtro BTC (`aroon_ema_equity.py`)

Solo long, uscita sotto EMA 90, ingresso Aroon 60 + EMA 90. Portafoglio a 1/N del capitale per moneta (N = 18, quota ferma in cassa), rendimento composto barra per barra, costo 0,12% per cambio di posizione, periodo 11/2020–10/2026. Filtro BTC: si entra solo se BTC chiude sopra la propria EMA 180 e si esce se scende sotto. Selezione = primi 3 anni, verifica = ultimi 3 (come README Bollinger). Tabella completa: `risultati_aroon_ema_equity.csv`.

| TF | Variante | Rend. 6 anni | Max DD | Calmar | Sharpe | Selezione | Verifica |
|---|---|---|---|---|---|---|---|
| 1d | senza filtro | +1.060% | −44,6% | 1,12 | 1,21 | +464% | +106% |
| 1d | con filtro BTC | +1.305% | −42,2% | 1,30 | 1,40 | +687% | +78% |
| 4h | senza filtro | +642% | −54,5% | 0,72 | 1,07 | +401% | +48% |
| 4h | con filtro BTC | **+758%** | **−33,3%** | **1,28** | 1,28 | +290% | **+120%** |
| – | buy & hold 1/N | +710% (1d) | −74,6% | 0,55 | 0,84 | +550% | +25% |

- Il filtro BTC riduce il drawdown su entrambi i timeframe e alza il rendimento sui 6 anni. Il miglioramento è netto sul 4h (drawdown −54% → −33%, verifica +48% → +120%); sull'1d è misto (la selezione migliora, la verifica peggiora da +106% a +78%).
- Rispetto al buy & hold il drawdown si dimezza circa (−33/−44% contro −75%), ma resta più alto del −21% del breakout Bollinger: qui non c'è uno stop loss.
- Confronto sul rapporto rendimento/drawdown composto (Calmar): 1d con filtro 1,30 e 4h con filtro 1,28, praticamente alla pari; il 4h ha il drawdown minore e la verifica migliore, l'1d ha meno operazioni (508 contro 2.775, quindi costi minori).
- Limiti: nessun stop loss, un solo parametro del filtro (EMA 180, non ottimizzata), periodo dominato dal rialzo 2020-21, ARB/OP/SUI con poca storia.

### Con stop loss 10%
Stop al 10% dal prezzo d'ingresso, valutato dentro la candela (uscita al livello, o all'apertura se la candela apre sotto). Dopo uno stop si rientra solo con un nuovo segnale.

| TF | Variante | Rend. 6 anni | Max DD | Calmar | Sharpe | Selezione | Verifica |
|---|---|---|---|---|---|---|---|
| 1d | filtro BTC, senza stop | +1.305% | −42,2% | 1,30 | 1,40 | +687% | +78% |
| 1d | filtro BTC, stop 10% | +986% | **−34,9%** | **1,38** | 1,44 | +507% | +79% |
| 1d | senza filtro, stop 10% | +930% | −37,8% | 1,24 | 1,28 | +399% | +107% |
| 4h | filtro BTC, senza stop | +758% | −33,3% | 1,28 | 1,28 | +290% | +120% |
| 4h | filtro BTC, stop 10% | +694% | −33,6% | 1,21 | 1,25 | +262% | +120% |

- Sull'1d lo stop abbassa il drawdown di circa 7 punti (−42% → −35%) e migliora Calmar e Sharpe, ma costa parte del rendimento (+1.305% → +986%).
- Sul 4h lo stop non serve: il drawdown resta uguale (−33%) e il rendimento cala leggermente. Con candele da 4 ore l'uscita sotto EMA scatta già prima che il 10% venga toccato.
