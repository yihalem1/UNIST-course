import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc



import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

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

# Concatenate the two data frames
data = pd.concat([data_2018.assign(year=2018), data_2019.assign(year=2019)])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


@app.callback(
    Output('world-map', 'figure'),
    Input('country-selector', 'value')
)
def update_map(selected_country):
    fig = go.Figure(data=go.Choropleth(
        locations=data['Country or region'], 
        z=data['Score'], 
        text=data['Country or region'], 
        locationmode='country names',
        colorscale='Blues',
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
    ))

    fig.update_layout(
        title_text='2018/2019 World Happiness Score',
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



app.layout = dbc.Container([
    html.H1("World Happiness Report Dashboard"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='country-selector',
                             options=[{'label': i, 'value': i} for i in data['Country or region'].unique()],
                             value='Finland',
                             multi=False,
                             clearable=False
                             ),
                width={'size': 4, 'offset': 4},
                ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='world-map'), width=6),
        dbc.Col(dcc.Graph(id='happiness-trend'), width=6),
    ]),
])


@app.callback(
    Output('happiness-trend', 'figure'),
    Input('country-selector', 'value')
)
def update_trend(selected_country):
    filtered_data = data[data['Country or region'] == selected_country]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_data['year'], y=filtered_data['Score'], mode='lines+markers', name='Happiness Score'))

    fig.update_layout(title='Happiness Score Over Time', xaxis_title='Year', yaxis_title='Score')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

