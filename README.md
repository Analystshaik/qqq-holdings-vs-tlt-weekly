# QQQ Holdings vs TLT — Weekly Relationship Engine

This is the same weekly TLT lead/lag framework as the Dow-30 version, expanded to the full **QQQ stock universe**.

## Core analysis kept identical

For every holding the engine calculates:

- 13-week, 26-week and 52-week correlation to TLT
- 26-week beta to TLT
- TLT lead correlations from 0 through 6 weeks
- Best historical TLT lead and lead correlation
- Best-lag beta
- Correlation stability
- 4-week and 13-week relative strength versus TLT
- Signed relationship score from -100 to +100
- Positive / inverse / low-or-unstable classification
- Follower Alert when TLT has moved but a historically lagging holding has not yet responded proportionally

`lag3_corr = Corr(Stock[t], TLT[t-3])`

A best lag of 3 therefore means TLT historically leads the stock by about three weekly bars.

## Universe refresh

`holdings_loader.py` refreshes the current QQQ stock constituent list from a public constituent table and saves a local cache:

`qqq_holdings.csv`

After the first successful refresh you can run offline from that cached list with:

```bat
python ibkr_backfill.py --no-refresh-holdings
```

The relationship engine analyzes stocks only; it does not treat cash or other non-stock fund basket items as securities to rank.

## Database

Default database:

`C:\Keystone\ibkr_production_data_engine_v2\data\ibkr_market_data.sqlite`

Tables added/used:

- `relationship_bars_day`
- `qqq_holdings_tlt_relationship_week`
- `qqq_holdings_tlt_relationship_snapshot`

The source daily table can be shared with your Dow/TLT project, while this package's analysis and snapshot tables are isolated.

## First run

Start TWS / IB Gateway with API access enabled.

```bat
pip install -r requirements.txt
python ibkr_backfill.py
python analyze_weekly.py
streamlit run dashboard.py
```

Or run:

```bat
run_all.bat
```

## Large-universe safety

Every completed symbol is committed to SQLite immediately. If IBKR, TWS, Windows, or the network interrupts a large run, rerunning does not discard already stored history.

The downloader uses:

- IBKR SMART routing
- ADJUSTED_LAST daily bars
- regular trading hours
- blank `endDateTime` to avoid the adjusted-last/end-date error
- 5 years of history
- retry/checkpoint behavior

## Follower Alert thresholds

Same initial rules as the Dow package:

- best TLT lead >= 1 week
- absolute best-lag correlation >= 0.45
- latest TLT weekly move >= 1%
- stock's realized weekly move differs from the lag-beta-implied move by at least 0.75%

These are configurable/tunable after you evaluate live results.

## Dashboard

The Streamlit dashboard contains:

1. Leadership Board
2. Follower Alerts
3. 0–6 week lag heatmap
4. Individual holding detail

Because QQQ contains many more stocks than the Dow, Leadership Board and heatmap have Top-N controls for readability.


## QQQ holdings refresh reliability

Version 1.1 includes two fixes:

- a structure-tolerant Nasdaq-100 table parser (handles ordinary and MultiIndex HTML columns)
- a bundled `qqq_holdings.csv` fallback, so the first run no longer depends on a successful website refresh

If the web page changes or is temporarily unavailable, the loader prints a warning and continues from the bundled/cache universe.

To deliberately skip the web refresh:

```bat
python ibkr_backfill.py --no-refresh-holdings
```

The engine ranks publicly tradable QQQ/Nasdaq-100 equity constituents. Non-tradable/private/cash fund basket items are not required for the stock-vs-TLT analysis; IBKR no-data symbols are skipped and reported without stopping the run.
