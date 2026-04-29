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
from dash.dependencies import Input, Output, State



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
    html.H1("World Happiness Report Visualization"),
    html.P("Welcome to our interactive World Happiness Report Visualization!",style={'fontSize': 20, 'color': 'black'}),
    html.P("Here, we've made it easy for you to navigate through the World Happiness Report data, spanning from 2015 to 2019. Choose your country of interest and dive into parameters such as Score, GDP per capita, Healthy life expectancy, Freedom, Generosity, and Perceptions of corruption."),
    html.P("Whether you're a researcher, or just someone curious about the factors affecting global happiness, we hope this tool sheds some light on your quest for understanding."),
    dbc.Row([
        dbc.Col(html.Label('Select a Country:', style={'fontSize': 15, 'marginBottom': '5px'}), width={'size': 2, 'offset': 0}),
        dbc.Col(dcc.Dropdown(id='country-selector',
                             options=[{'label': i, 'value': i} for i in data['Country'].unique()],
                             value='Finland',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 2, 'offset': 0},
                ),
        dbc.Col(html.Label('Choose a Parameter to Analyze:', style={'fontSize': 15}), width={'size': 3, 'offset': 0}),
        dbc.Col(dcc.Dropdown(id='variable-selector',
                             options=[{'label': i, 'value': i} for i in ['Score', 'GDP per capita', 'Healthy life expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']],
                             value='Score',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 3, 'offset': 0},
                ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Slider(
            id='year-slider',
            min=data['year'].min(),
            max=data['year'].max(),
            value=2019,#data['year'].max(),
            marks={str(year): str(year) for year in data['year'].unique()},
            step=None
        ), width={'size': 4, 'offset': 3}
        ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='world-map'), width=6),
        dbc.Col(dcc.Graph(id='happiness-trend'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='correlation-heatmap'), width=6),
        dbc.Col(dcc.Graph(id='bar-chart'), width=6),
    ]),
    dcc.Store(id='selected-country'),

])
@app.callback(
    Output('world-map', 'figure'),
    [Input('year-slider', 'value'),
     Input('variable-selector', 'value')]
)
def update_map(selected_year, selected_variable):
    filtered_data = data[data['year'] == selected_year]
    fig = go.Figure(data=go.Choropleth(
        locations=filtered_data['Country'], # spatial locations
        z = filtered_data[selected_variable], # data to be color-coded
        locationmode = 'country names', # set of locations match entries in `locations`
        colorscale = 'Blues',
        colorbar_title = "Happiness",
    ))

    fig.update_layout(
        title_text = 'World Happiness Map',
        geo_scope='world',  # limit map scope to USA
    )

    return fig

@app.callback(
    Output('happiness-trend', 'figure'),
    [Input('selected-country', 'data'),
     Input('country-selector', 'value'),
     Input('variable-selector', 'value')]
)
def update_trend(selected_country, selected_country_from_dropdown, selected_variable):
    # Use callback context to identify which input triggered the callback
    ctx = dash.callback_context

    # If the callback was triggered by the map (i.e., 'selected-country' input)
    if ctx.triggered and 'selected-country' in ctx.triggered[0]['prop_id']:
        # Prioritize the country selected from the map
        selected_country = selected_country

    # If the callback was triggered by the dropdown (i.e., 'country-selector' input)
    elif ctx.triggered and 'country-selector' in ctx.triggered[0]['prop_id']:
        # Use the country selected from the dropdown
        selected_country = selected_country_from_dropdown

    # If no country was selected from either the map or the dropdown
    if selected_country is None:
        return go.Figure()

    # Update the line chart
    filtered_data = data[data['Country'] == selected_country]
    fig = go.Figure(data=go.Scatter(x=filtered_data['year'], y=filtered_data[selected_variable], mode='lines+markers'))
    fig.update_layout(
        title=f'Trend Over Years for {selected_country} ({selected_variable})',
        xaxis_title='Year',
        yaxis_title='Happiness Score'
    )

    return fig




@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('year-slider', 'value')]
)
def update_heatmap(selected_year):
    filtered_data = data[data['year'] == selected_year]
    corr = filtered_data.corr()

    fig = go.Figure(data=go.Heatmap(
                   z=corr,
                   x=corr.columns,
                   y=corr.columns,
                   hoverongaps=False,
                   colorscale='YlGnBu'))  # changed colorscale to 'YlGnBu'

    fig.update_layout(title=f'Correlation Heatmap for {selected_year}')  # added a dynamic title

    return fig


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_barchart(selected_year):
    filtered_data = data[data['year'] == selected_year]
    top10_countries = filtered_data.nlargest(10, 'Score')  # changed to nlargest
    fig = px.bar(top10_countries, y='Country', x='Score', orientation='h', 
                 hover_data=['Score'], text='Score')  # added text='Score'
    fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')  # formatting the text inside bars

    # updated title to include selected year
    fig.update_layout(
        title=f'Top 10 Happiest Countries in {selected_year}',
        xaxis_title='Happiness Score',
        yaxis_title='Country'
    )

    fig.update_yaxes(autorange="reversed")  # reverse the ordering of countries

    return fig




@app.callback(
    Output('selected-country', 'data'),
    [Input('world-map', 'clickData')]
)
def update_selected_country(clickData):
    if clickData is None:
        return None
    else:
        # This is the country that was clicked
        return clickData['points'][0]['location']
    
@app.callback(
    Output('year-slider', 'value'),
    [Input('happiness-trend', 'clickData')]
)
def update_year_from_trend(clickData):
    if clickData is None:
        return None
    else:
        clicked_year = clickData['points'][0]['x']
        return clicked_year


@app.callback(
    Output('country-selector', 'value'),
    [Input('bar-chart', 'clickData')]
)
def update_country_from_barchart(clickData):
    if clickData is None:
        return None
    else:
        # Extract the country from the clicked data on the bar chart
        clicked_country = clickData['points'][0]['y']
        return clicked_country

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
