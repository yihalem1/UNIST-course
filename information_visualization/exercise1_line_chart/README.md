# Exercise 1 — Life Expectancy Line Chart (D3.js)

Multi-line chart of life expectancy over ~60 years, restricted to the
**5 countries with the largest min/max life-expectancy gap**.

## Task

Given a CSV with one row per `(country_code, country_name, year, value)`:

1. For each country compute `max(value) - min(value)`.
2. Sort countries by that gap, descending.
3. Pass the top 5 to `drawLineChart(...)`.
4. Plot one line per country: x = year, y = life expectancy (0 → max).
5. Color palette: `['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']`.
6. Label each line at its right endpoint, in the matching color.
7. Strip thousand-separators from year tick labels.

## Files

| File | Purpose |
|---|---|
| [index.html](index.html) | D3 v7 host page |
| [js/main.js](js/main.js) | Filtering + line-chart rendering |
| [data/life_expectancy_by_country.csv](data/life_expectancy_by_country.csv) | Input dataset |
| [example1.png](example1.png) | Reference visualization (countries shown are illustrative) |

## How to run

Open `index.html` from a local web server (D3 needs `fetch`, not `file://`):

```bash
python -m http.server 8000
# then visit http://localhost:8000/
```
