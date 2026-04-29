import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import seaborn as sns
import numpy as np
import plotly.express as px
import os


def process_data(file_name):
    # Check if file exists
    if os.path.isfile(file_name):
        data = pd.read_csv(file_name)
        columns_to_rename = {
            'Country or region': 'Country',
            'Freedom to make life choices': 'Freedom',
        }
        # Check if columns are in dataframe
        if all(item in data.columns for item in ['Social support'] + list(columns_to_rename.keys())):
            data_processed = data.drop('Social support', axis=1)
            data_processed.rename(columns=columns_to_rename, inplace=True)
            return data_processed
        else:
            print(f"Error: One or more columns not found in {file_name}")
            return None
    else:
        print(f"Error: File {file_name} not found.")
        return None

# Process 2019.csv and 2018.csv
data0_processed = process_data('2019.csv')
data1_processed = process_data('2018.csv')

# Data 2: 2017.csv
data2 = pd.read_csv('2017.csv')
data2_processed = data2[['Country', 'Happiness.Rank', 'Happiness.Score',
                         'Economy..GDP.per.Capita.', 'Health..Life.Expectancy.',
                         'Freedom', 'Generosity', 'Trust..Government.Corruption.']]
data2_processed.rename(columns={'Happiness.Rank': 'Overall rank',
                                'Happiness.Score': 'Score',
                                'Economy..GDP.per.Capita.': 'GDP per capita',
                                'Health..Life.Expectancy.': 'Healthy life expectancy',
                                'Trust..Government.Corruption.': 'Perceptions of corruption'}, inplace=True)

# Data 3: 2016.csv
data3 = pd.read_csv('2016.csv')
data3_processed = data3[['Country', 'Happiness Rank', 'Happiness Score',
                         'Economy (GDP per Capita)', 'Health (Life Expectancy)',
                         'Freedom', 'Generosity', 'Trust (Government Corruption)']]
data3_processed.rename(columns={'Happiness Rank': 'Overall rank',
                                'Happiness Score': 'Score',
                                'Economy (GDP per Capita)': 'GDP per capita',
                                'Health (Life Expectancy)': 'Healthy life expectancy',
                                'Trust (Government Corruption)': 'Perceptions of corruption'}, inplace=True)

# Data 4: 2015.csv
data4 = pd.read_csv('2015.csv')
data4_processed = data4[['Country', 'Happiness Rank', 'Happiness Score',
                         'Economy (GDP per Capita)', 'Health (Life Expectancy)',
                         'Freedom', 'Generosity', 'Trust (Government Corruption)']]
data4_processed.rename(columns={'Happiness Rank': 'Overall rank',
                                'Happiness Score': 'Score',
                                'Economy (GDP per Capita)': 'GDP per capita',
                                'Health (Life Expectancy)': 'Healthy life expectancy',
                                'Trust (Government Corruption)': 'Perceptions of corruption'}, inplace=True)
data0_processed = data0_processed.assign(year=2019)
data1_processed = data1_processed.assign(year=2018)
data2_processed = data2_processed.assign(year=2017)
data3_processed = data3_processed.assign(year=2016)
data4_processed = data4_processed.assign(year=2015)

# Concatenate the data frames
data = pd.concat([data0_processed, data1_processed, data2_processed, data3_processed, data4_processed])

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("World Happiness Report Dashboard"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='country-selector',
                             options=[{'label': i, 'value': i} for i in data['Country'].unique()],
                             value='Finland',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 1},
                ),
        dbc.Col(dcc.Dropdown(id='variable-selector',
                             options=[{'label': i, 'value': i} for i in ['Score', 'GDP per capita', 'Healthy life expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']],
                             value='Score',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 1},
                ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Slider(id='year-slider',
                           min=data['year'].min(),
                           max=data['year'].max(),
                           value=data['year'].max(),
                           marks={str(year): str(year) for year in data['year'].unique()},
                           step=None), width=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='variable1-selector',
                             options=[{'label': i, 'value': i} for i in ['Score', 'GDP per capita', 'Healthy life expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']],
                             value='Score',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 1},
                ),
        dbc.Col(dcc.Dropdown(id='variable2-selector',
                             options=[{'label': i, 'value': i} for i in ['Score', 'GDP per capita', 'Healthy life expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']],
                             value='GDP per capita',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 1},
                ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='world-map'), width=6),
        dbc.Col(dcc.Graph(id='happiness-trend'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='score-distribution'), width=4),
        dbc.Col(dcc.Graph(id='correlation-heatmap'), width=4),
        dbc.Col(dcc.Graph(id='bar-chart'), width=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-plot'), width=6),
    ]),
])
@app.callback(
    Output('world-map', 'figure'),
    [Input('country-selector', 'value'),
     Input('year-slider', 'value'),
     Input('variable-selector', 'value')]
)
def update_map(selected_country, selected_year, selected_variable):
    filtered_data = data[data['year'] == selected_year]

    fig = go.Figure(data=go.Choropleth(
        locations=filtered_data['Country'], 
        z=filtered_data[selected_variable], 
        text=filtered_data.apply(lambda row: f"{row['Country']}: {row[selected_variable]}", axis=1),
        locationmode='country names',
        colorscale='Blues',
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        hoverinfo='text',
    ))

    fig.update_layout(
        autosize=False,
        width=700,
        height=500,
        title_text=f'{selected_year} World {selected_variable}',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        annotations=[dict(
            x=0.55,
            y=0.1,
            xref='paper',
            yref='paper',
            showarrow=False
        )]
    )

    return fig

@app.callback(
    Output('happiness-trend', 'figure'),
    [Input('country-selector', 'value'),
     Input('year-slider', 'value'),
     Input('world-map', 'clickData'),
     Input('variable-selector', 'value')]
)
def update_trend(selected_country, selected_year, clickData, selected_variable):
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

    filtered_data = data[data['Country'] == selected_country]
    fig = go.Figure(data=go.Scatter(x=filtered_data['year'], y=filtered_data[selected_variable], mode='lines+markers'))

    fig.update_layout(title=f'{selected_variable} Trend for {selected_country}', xaxis_title='Year', yaxis_title=selected_variable)

    return fig

@app.callback(
    Output('score-distribution', 'figure'),
    [Input('year-slider', 'value'),
     Input('variable-selector', 'value')]
)
def update_distribution(selected_year, selected_variable):
    filtered_data = data[data['year'] == selected_year]
    
    # Clean your data here
    filtered_data = filtered_data[~filtered_data[selected_variable].isnull()]  # remove NaNs
    filtered_data = filtered_data[np.isfinite(filtered_data[selected_variable])]  # remove infs and -infs
    
    # Add a check if the data is empty
    if not filtered_data.empty:
        fig = ff.create_distplot([filtered_data[selected_variable]], [selected_variable], show_hist=False)
        fig.update_layout(title=f'{selected_variable} Distribution')
    else:
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected year and variable.",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False)
        
    return fig

# I assume that the callbacks for correlation-heatmap and bar-chart are the same as your provided code, thus skipping them here

@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('year-slider', 'value')]
)
def update_heatmap(selected_year):
    filtered_data = data[data['year'] == selected_year]

    correlation = filtered_data[['Score', 'GDP per capita', 'Healthy life expectancy', 
                                 'Freedom', 'Generosity', 'Perceptions of corruption']].corr()

    fig = go.Figure(data=go.Heatmap(
                   z=correlation,
                   x=list(correlation.columns),
                   y=list(correlation.columns),
                   hoverongaps = False, colorscale='Viridis'))

    fig.update_layout(title='Correlation Heatmap')

    return fig

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_barchart(selected_year):
    filtered_data = data[data['year'] == selected_year]
    top_countries = filtered_data.sort_values('Score', ascending=False).head(10)

    fig = go.Figure(data=[go.Bar(
                x=top_countries['Country'],
                y=top_countries['Score'],
                text=top_countries['Score'],
                textposition='auto'
            )])

    fig.update_layout(title='Top 10 Countries')

    return fig


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('year-slider', 'value'),
     Input('world-map', 'clickData'),
     Input('variable1-selector', 'value'),
     Input('variable2-selector', 'value')]
)
def update_scatter(selected_year, clickData, selected_variable1, selected_variable2):
    filtered_data = data[data['year'] == selected_year]

    if clickData is not None:
        selected_country = clickData['points'][0]['location']
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]

    fig = px.scatter(filtered_data, x=selected_variable1, y=selected_variable2)

    fig.update_layout(title=f'{selected_variable1} vs {selected_variable2}')

    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
