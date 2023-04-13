import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc


# get the COVID data and normalize the json data
resp = requests.get('https://data.cdc.gov/resource/pwn4-m3yp.json?$limit=50000').json()
df = pd.json_normalize(resp)
# convert string dates to datetime
df[['date_updated', 'start_date', 'end_date']] = df[['date_updated', 'start_date', 'end_date']].apply(pd.to_datetime)
# convert string numbers to float
df[df.columns[4:]] = df[df.columns[4:]].astype(float)
most_current_df = df.iloc[df.groupby('state')['start_date'].idxmax()]

# create the map
covid_map = px.choropleth(most_current_df,
                          locations='state',
                          locationmode="USA-states",
                          scope="usa",
                          color='tot_cases',
                          color_continuous_scale=px.colors.diverging.RdYlGn_r,
                          labels={'tot_cases': 'Total Cases'})
covid_map.update_layout(dict(height=400))

external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Center(html.H1('COVID-19 Total Cases')),
    dcc.Graph(id="covid-map", figure=covid_map),
    html.Div(id='covid-state-data')
])


@app.callback(Output('covid-state-data', 'children'),
              Input('covid-map', 'clickData'))
def state_click(click_data):
    if click_data:
        # get the name of the state clicked
        click_loc = click_data['points'][0]['location']
        # filter covid df
        state_df = df[df['state'].eq(click_loc)].sort_values('start_date')
        # create the new line + bar graph for the state clicked
        state_fig = make_subplots(specs=[[{"secondary_y": True}]])

        state_fig.add_trace(
            go.Scatter(x=state_df['start_date'], y=state_df['tot_cases'],
                       name=f'{click_loc} Total Cases', mode='lines'),
            secondary_y=False
        )

        state_fig.add_trace(
            go.Bar(x=state_df['start_date'], y=state_df['new_cases'], name=f'{click_loc} New Cases'),
            secondary_y=True
        )

        state_fig.update_layout(dict(hovermode='x unified', title=f'{click_loc} COVID-19 Data', height=400))

        return dcc.Graph(id=f'{click_loc}-covid-data', figure=state_fig)


if __name__ == '__main__':
    app.run_server(debug=False)
