# BBStrategy – SMA + Bande di Bollinger

Strategia Pine (TradingView) `sma_bande_trend.pine` con due modalità:

- **Breakout (consigliata, predefinita)**: solo long. Entra quando la candela chiude sopra la banda superiore *e* sopra la EMA 180; esce quando chiude sotto la SMA o allo stop loss in percentuale (10%).
- **Originale (armata)**: la strategia creata inizialmente (candela rossa sotto la SMA poi verde sopra, uscite sulle bande), invariata.

Parametri di partenza: SMA 50, bande 3,0 deviazioni standard, EMA 180, stop 10%, timeframe **4h**.
Lo short sotto la EMA 180 è disponibile ma **disattivato**: nei test peggiora il risultato.

> Lo script Pine non è stato compilato su TradingView da chi ha scritto la modifica: al primo caricamento controlla la console di Pine.

## Paniere

`paniere.json` elenca le 18 monete testate (coppie USDT su Binance), derivate dall'universo del progetto AHA senza ATOM e INJ.
ATOM e INJ sono state escluse perché negative nel periodo di selezione (11/2020–10/2023) e senza recupero nel periodo di verifica (11/2023–10/2026). ARB, OP e SUI hanno meno di 3 anni di storia e non sono valutabili con quel criterio.

## Risultati dei backtest

Dati: candele Binance spot, 11/2020–10/2026 (17 monete con storia completa; per gli ultimi 2 anni 20 monete). Costo 0,12% per ogni cambio di posizione (commissione 0,1% più slippage 0,02%). Portafoglio a **1/N del capitale per moneta**, con la quota delle monete ferme lasciata in cassa: rendimento, drawdown e Sharpe sono sul capitale totale, con esposizione ridotta.

**Breakout solo long, 4h, stop dentro la candela** (rendimento % / drawdown massimo):

| Configurazione | 17 monete, 6 anni | 17 monete, ultimi 3 anni | 15 monete (senza ATOM e INJ), ultimi 3 anni |
|---|---|---|---|
| SMA 50, bande 3, stop 5% | +210% / −21% | +76% / −13% | +103% / −13% |
| SMA 50, bande 3, stop 10% (predefinita) | +359% / −23% | +83% / −16% | +107% / −16% |
| SMA 20, bande 2,5, stop 5% | +187% / −21% | +47% / −21% | +62% / −20% |
| SMA 20, bande 3, senza stop | +265% / −17% | +45% / −17% | +52% / −17% |

Buy & hold sullo stesso paniere: +882% sui 6 anni (grazie al rialzo del 2021), −80% di drawdown, −62% negli ultimi 2 anni. La strategia è **difensiva**: nei rialzi rende molto meno del semplice tenere le monete, ma limita i drawdown (circa −13% / −23% contro −80%).

**Short sotto la EMA 180** (SMA 50, bande 3, stop 5%, 4h, 6 anni): solo short −51% (drawdown −61%); long+short +150% (drawdown −35%) contro +406% del solo long con stop sulla chiusura. Lo short non guadagna neanche nei ribassi.

## Limiti da tenere presenti

- **Ottimismo dei risultati.** La configurazione (SMA 50, bande 3) è stata scelta tra circa 36 varianti guardando l'intero periodo, quindi il periodo di verifica non è fuori campione in senso stretto. I numeri assoluti vanno considerati ottimistici.
- **Survivorship bias.** Il paniere è quello esistente oggi: monete fallite o delistate nel 2021–2024 non ci sono.
- **Poca storia.** Sei anni, con un solo ciclo completo di mercato. Nei test su 1, 5, 15 e 30 minuti la strategia non funziona (costi troppo alti rispetto ai movimenti).
- **Esecuzione simulata.** Gli ingressi avvengono alla chiusura; le uscite alla SMA sono valutate sulla chiusura; gli stop sono simulati dentro la candela ma senza ordine intrabar tra stop e rientro. Il confronto è sensibile a commissioni e slippage reali.
- **Verifica dei calcoli.** Il motore a barre chiuse è stato riscritto da zero in modo indipendente da un sotto-agente: gli scarti sulle serie di rendimento sono zero.
