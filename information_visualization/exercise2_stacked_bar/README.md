# Exercise 2 — Vaccination Rates Stacked Bar (D3.js)

Horizontal stacked bar chart of COVID-19 vaccination rates for the
**top-15 countries** by share of people vaccinated.

## Task

Source: Our World in Data COVID-19 dataset (`owid-covid-data.csv`),
1 row per `(location, date)`.

For each country, take the **most recent** record and compute:

- `fully_pct       = people_fully_vaccinated / population`
- `partially_pct   = (people_vaccinated - people_fully_vaccinated) / population`

Then:

1. Drop countries whose total vaccination rate exceeds 100% (data noise).
2. Sort by total vaccination rate, descending; keep the top 15.
3. Draw one horizontal stacked bar per country:
   - Left segment = fully vaccinated, color `#7bccc4`.
   - Right segment = partially vaccinated, color `#2b8cbe`.
4. X-axis: 0–100% with even ticks. Y-axis: country names.
5. Label each segment with its percentage — **inside** the bar for the
   right segment, **outside** for the left.

## Files

| File | Purpose |
|---|---|
| [index.html](index.html) | D3 host page |
| [js/main.js](js/main.js) | Data processing + stacked bar rendering |
| [example2.png](example2.png) | Reference visualization (countries shown are illustrative) |

> The OWID dataset (`data/owid-covid-data.csv`, ~hundreds of MB) is **not
> committed**. Download the latest copy from
> https://github.com/owid/covid-19-data/tree/master/public/data and drop
> it into `data/` to run.

## How to run

```bash
python -m http.server 8000
# visit http://localhost:8000/
```
