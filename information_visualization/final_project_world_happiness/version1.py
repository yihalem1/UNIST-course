import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# Data 1: 2019.csv
data0 = pd.read_csv('2019.csv')
data0_processed = data0.drop('Social support', axis=1)
data0_processed.rename(columns={'Country or region': 'Country'}, inplace=True)

# Data 1: 2018.csv
data1 = pd.read_csv('2018.csv')
data1_processed = data1.drop('Social support', axis=1)
data1_processed.rename(columns={'Country or region': 'Country'}, inplace=True)

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

# Define the app layout
app.layout = dbc.Container([
    html.H1("World Happiness Report Dashboard"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='country-selector',
                             options=[{'label': i, 'value': i} for i in data['Country'].unique()],
                             value='Finland',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 4},
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
        dbc.Col(dcc.Graph(id='world-map'), width=6),
        dbc.Col(dcc.Graph(id='happiness-trend'), width=6),
    ]),
])

@app.callback(
    Output('world-map', 'figure'),
    [Input('country-selector', 'value'),
     Input('year-slider', 'value')]
)
def update_map(selected_country, selected_year):
    filtered_data = data[data['year'] == selected_year]

    fig = go.Figure(data=go.Choropleth(
        locations=filtered_data['Country'], 
        z=filtered_data['Score'], 
        text=filtered_data.apply(lambda row: f"{row['Country']}: {row['Score']}", axis=1),
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
        title_text=f'{selected_year} World Happiness Score',
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


# Define the callback to update the trend chart
@app.callback(
    Output('happiness-trend', 'figure'),
    [Input('country-selector', 'value'),
     Input('year-slider', 'value')]
)
def update_trend(selected_country, selected_year):
    filtered_data = data[data['Country'] == selected_country]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_data['year'], y=filtered_data['Score'], mode='lines+markers', name='Happiness Score'))

    fig.update_layout(title='Happiness Score Over Time', xaxis_title='Year', yaxis_title='Score')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
