# Final Project — World Happiness Report Dashboard

A multi-view interactive dashboard exploring the **World Happiness Report**
across 2015–2019. Built with Python, **Dash**, **Plotly**, and
**dash-bootstrap-components**.

## What it does

The dashboard unifies five years of country-level happiness data
(`2015.csv` … `2019.csv`) into a single schema (the raw CSVs use slightly
different column names each year, so they're harmonized in code) and lets
the user explore it through linked views:

- **Country dropdown** — pick a focus country.
- **Variable dropdown** — pick a metric: `Score`, `GDP per capita`,
  `Healthy life expectancy`, `Freedom`, `Generosity`,
  `Perceptions of corruption`.
- **Year slider** — 2015 → 2019.
- **World map (choropleth)** — chosen variable, chosen year, all countries.
- **Trend line** — selected country's metric over 2015–2019.
- **Correlation heatmap** — pairwise correlations among the metrics.
- **Bar chart** — top-N countries on the chosen metric for the chosen year.

## Files

| File | Purpose |
|---|---|
| [version6.py](version6.py) | **Final** dashboard (latest iteration) — this is the version submitted |
| [version5.py](version5.py) | Prior iteration |
| [version4.py](version4.py) | Prior iteration |
| [version3.py](version3.py) | Prior iteration |
| [version2.py](version2.py) | Prior iteration |
| [version1.py](version1.py) | Earliest end-to-end version |
| [dash_app.py](dash_app.py) | Standalone Dash skeleton used while prototyping |
| [infovis.py](infovis.py) | Data-loading / preprocessing helpers shared across versions |
| [2015.csv](2015.csv) – [2019.csv](2019.csv) | Source data: World Happiness Report 2015–2019 |
| [report.pdf](report.pdf) | Written report (design rationale, screenshots, discussion) |

## How to run

```bash
pip install dash dash-bootstrap-components plotly pandas seaborn numpy
python version6.py
# open http://127.0.0.1:8050/ in a browser
```

> The `dash_core_components` / `dash_html_components` imports are the
> legacy split-package style (Dash < 2.0). On newer Dash you can either
> pin `dash==1.21.0` or rewrite the imports to `from dash import dcc, html`.

See [report.pdf](report.pdf) for the full write-up.
