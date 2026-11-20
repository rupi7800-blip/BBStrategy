# BBStrategy – SMA + Bande di Bollinger

Strategia Pine (TradingView) `sma_bande_trend.pine` con due modalità:

- **Breakout (consigliata, predefinita)**: solo long. Entra quando la candela chiude sopra la banda superiore *e* sopra la EMA 180 *e* BTC è sopra la propria EMA (filtro di mercato); esce quando chiude sotto la SMA, allo stop loss in percentuale (10%) o se BTC scende sotto la sua EMA.
- **Originale (armata)**: la strategia creata inizialmente (candela rossa sotto la SMA poi verde sopra, uscite sulle bande), invariata.

Parametri di partenza: SMA 50, bande 3,0 deviazioni standard, EMA 180, stop 10%, filtro di mercato BTC attivo, timeframe **4h**.
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
| SMA 50, bande 3, stop 10% (senza filtro BTC) | +359% / −23% | +83% / −16% | +107% / −16% |
| SMA 20, bande 2,5, stop 5% | +187% / −21% | +47% / −21% | +62% / −20% |
| SMA 20, bande 3, senza stop | +265% / −17% | +45% / −17% | +52% / −17% |

Buy & hold sullo stesso paniere: +882% sui 6 anni (grazie al rialzo del 2021), −80% di drawdown, −62% negli ultimi 2 anni. La strategia è **difensiva**: nei rialzi rende molto meno del semplice tenere le monete, ma limita i drawdown (circa −6% / −23% contro −80%).

**Short sotto la EMA 180** (SMA 50, bande 3, stop 5%, 4h, 6 anni): solo short −51% (drawdown −61%); long+short +150% (drawdown −35%) contro +406% del solo long con stop sulla chiusura. Lo short non guadagna neanche nei ribassi.

## Profili con drawdown più basso

Il filtro di mercato (BTC sopra la propria EMA 180, con chiusura delle posizioni quando si spegne) abbassa il drawdown senza ridurre il rendimento. Allargare le bande (3,5 invece di 3) lo abbassa ancora, ma riduce il rendimento. Test sul paniere da 15 monete (senza ATOM e INJ), 4h, stop 10% dentro la candela, costo 0,12% per cambio di posizione, 11/2020–10/2026 (periodo di selezione: primi 3 anni; verifica: ultimi 3):

| Profilo | Impostazioni | Selezione: rend. / DD | Verifica: rend. / DD | 6 anni: rend. / DD | Sharpe | Anni positivi |
|---|---|---|---|---|---|---|
| Riferimento (senza filtro BTC) | SMA 50, bande 3 | +189% / −21% | +107% / −16% | +499% / −21% | 1,5 | 5 su 6 |
| **A – Equilibrata (predefinita)** | SMA 50, bande 3, filtro BTC | +178% / −13% | +124% / −13% | +524% / −13% | 1,6 | 6 su 6 |
| B – Prudente | SMA 50, bande 3,5, filtro BTC | +114% / −11% | +64% / −8% | +251% / −11% | 1,5 | 6 su 6 |
| C – Molto prudente | SMA 30, bande 3,5, filtro BTC | +109% / −6% | +45% / −6% | +203% / −6% | 1,7 | 6 su 6 |

Rendimenti per anno (11/2020–10/2026, il primo è parziale: parte dopo 250 barre): A: +148, +9, +3, +30, +45, +19; C: +76, +6, +12, +14, +12, +13.

La zona dei parametri è stabile (variando SMA 30/50, bande 2,5–3,5, stop 7–12% e EMA 180/300 i risultati cambiano in modo graduale). Il rapporto è chiaro: più si abbassa il drawdown, più cala il rendimento. Non ho incluso il dimensionamento in base alla volatilità: riduce il drawdown ma in modo meno netto del filtro BTC.

## Limiti da tenere presenti

- **Ottimismo dei risultati.** La configurazione (SMA 50, bande 3) è stata scelta tra circa 36 varianti guardando l'intero periodo, e il filtro BTC e i profili tra 432 varianti (selezione sui primi 3 anni, ma la verifica sugli ultimi 3 non è del tutto indipendente), quindi il periodo di verifica non è fuori campione in senso stretto. I numeri assoluti vanno considerati ottimistici.
- **Survivorship bias.** Il paniere è quello esistente oggi: monete fallite o delistate nel 2021–2024 non ci sono.
- **Poca storia.** Sei anni, con un solo ciclo completo di mercato. Nei test su 1, 5, 15 e 30 minuti la strategia non funziona (costi troppo alti rispetto ai movimenti).
- **Esecuzione simulata.** Gli ingressi avvengono alla chiusura; le uscite alla SMA sono valutate sulla chiusura; gli stop sono simulati dentro la candela ma senza ordine intrabar tra stop e rientro. Il confronto è sensibile a commissioni e slippage reali.
- **Verifica dei calcoli.** Il motore a barre chiuse è stato riscritto da zero in modo indipendente da un sotto-agente: gli scarti sulle serie di rendimento sono zero. Il motore usato per i profili con filtro BTC (stop dentro la candela) non è stato controllato da un sotto-agente: riproduce però il riferimento senza filtro (+107% / −16% nel periodo di verifica), uguale ai test già verificati.

## Strategia Aroon + EMA

Seconda strategia sullo stesso paniere: Aroon 60 e EMA 90, solo long, con filtro BTC sopra la propria EMA 180.
Ingresso alla prima candela che chiude sopra la EMA con Aroon rialzista; uscita alla chiusura sotto la EMA o se il filtro BTC si spegne.
Tre sistemi (script Pine, stessa logica, impostazioni diverse):

- `aroon_ema_1d_stop.pine`: timeframe **1d**, stop loss 10% (rendimento +986% su 6 anni, drawdown −34,9%, Calmar 1,38).
- `aroon_ema_1d_nostop.pine`: timeframe **1d**, senza stop (rendimento +1.305%, drawdown −42,2%, Calmar 1,30; ultimi 3 anni +78%).
- `aroon_ema_4h_nostop.pine`: timeframe **4h**, senza stop (rendimento +758%, drawdown −33,3%, Calmar 1,28; ultimi 3 anni +120%).

Backtest e dettagli: `backtest/RISULTATI_AROON_EMA.md`, script `backtest/aroon_ema.py` e `backtest/aroon_ema_equity.py`.
> Come per l'altro script, i Pine non sono stati compilati su TradingView dall'autore: al primo caricamento controlla la console di Pine.
