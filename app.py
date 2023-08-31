import graphs
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash.dependencies import Input, Output
from dash import dcc, html, ctx
import dash_bootstrap_components as dbc

card_css = {'margin': '10px 10px 10px 0px'}

external_stylesheets = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    dbc.Container([
        # cards / graphs layout
        html.Div([
            # row 1
            dbc.CardGroup([
                # covid map
                dbc.Card([
                    dcc.Graph(id="covid-map", figure=graphs.covid_map)
                ], style=card_css),
                # state graph
                dbc.Card([
                    html.Div([dbc.Button('Reset', id='reset-button', n_clicks=0)],
                             style={'margin-right': '10px', 'margin-top': '10px',
                                    'margin-bottom': '10px', 'text-align': 'right'}),
                    html.Div(id='covid-state-data')
                ], style=card_css)
            ], ),
            # row 2
            dbc.CardGroup([
                # covid death graph
                dbc.Card([
                    dcc.Graph(id='covid-deaths', figure=graphs.death_fig)
                ], style={'margin-right': '10px'})
            ])
        ]),
    ], fluid=True)
])


# callback function to set the new graph when a state is clicked
@app.callback(Output('covid-state-data', 'children'),
              Input('covid-map', 'clickData'),
              Input('reset-button', 'n_clicks'))
def state_click(state_clicks, n_clicks):
    # reset data if reset button is clicked
    if ctx.triggered_id == 'reset-button':
        return dcc.Graph(id='all-covid-data', figure=graphs.all_data_fig)
    # else if a state is clicked then get the state data
    elif state_clicks:
        # get the name of the state clicked
        click_loc = state_clicks['points'][0]['location']
        # filter covid df
        df = graphs.df
        state_df = df[df['state'].eq(click_loc)].sort_values('start_date')
        # create the new line + bar graph for the state clicked
        state_fig = make_subplots(specs=[[{"secondary_y": True}]])
        # create the graph
        state_fig.add_trace(
            go.Scatter(x=state_df['start_date'], y=state_df['tot_cases'],
                       name=f'{click_loc} Total Cases', mode='lines', showlegend=False),
            secondary_y=False
        )

        state_fig.add_trace(
            go.Bar(x=state_df['start_date'], y=state_df['new_cases'], name=f'{click_loc} New Cases', showlegend=False),
            secondary_y=True
        )

        state_fig.update_layout(dict(hovermode='x unified',
                                     title=f'{click_loc} COVID-19 Cases',
                                     template='plotly_dark',
                                     plot_bgcolor='rgba(0, 0, 0, 0)',
                                     paper_bgcolor='rgba(0, 0, 0, 0)'
                                     ))

        return dcc.Graph(id=f'{click_loc}-covid-data', figure=state_fig)
    # else just use all the data
    else:
        return dcc.Graph(id='all-covid-data', figure=graphs.all_data_fig)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
