# Exercise 4 — Bubble / Scatter Chart (D3.js)

Bubble chart of demographic indicators for 1999, joining three World Bank
CSVs by country:

- **x** — life expectancy (years)
- **y** — fertility rate (births per woman)
- **bubble radius** — `sqrt(population / 1e7)`

## Files

| File | Purpose |
|---|---|
| [index.html](index.html) | D3 v5 host page |
| [ex_4.js](ex_4.js) | Loads the three CSVs, joins them, renders the SVG scatter |
| [fertility_rate.csv](fertility_rate.csv) | Fertility rate per country / year |
| [life_expectancy.csv](life_expectancy.csv) | Life expectancy per country / year |
| [population.csv](population.csv) | Population per country / year |

## How to run

```bash
python -m http.server 8000
# visit http://localhost:8000/
```
