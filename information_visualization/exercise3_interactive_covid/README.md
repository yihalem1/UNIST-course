# Exercise 3 — Interactive COVID-19 Dashboard (D3.js)

Interactive multi-country viewer over the OWID COVID-19 dataset, with
runtime controls for country selection, date range, and chart type.

## Features

- **Country checkboxes** — pick any subset of countries; lines / bars are
  added or removed live.
- **Date range** — `Start Date` and `End Date` inputs filter the series.
- **Chart toggle** — switch between line chart and bar chart on the same
  data.
- **Color legend** keyed by country, matching line colors.
- Underlying metric: share of `people_vaccinated` and
  `people_fully_vaccinated` over `population`.

## Files

| File | Purpose |
|---|---|
| [index.html](index.html) | Page layout, controls, D3 v6 |
| [exercise3.js](exercise3.js) | Data load, selection state, render dispatch |

> The OWID dataset (`owid-covid-data.csv`) is not committed. Download it
> from the OWID repo and place it next to `index.html` to run.

## How to run

```bash
python -m http.server 8000
# visit http://localhost:8000/
```
