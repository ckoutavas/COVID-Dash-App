import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# get the COVID data and normalize the json data
resp = requests.get('https://data.cdc.gov/resource/pwn4-m3yp.json?$limit=50000').json()
df = pd.json_normalize(resp)
# convert string dates to datetime
df[['date_updated', 'start_date', 'end_date']] = df[['date_updated', 'start_date', 'end_date']].apply(pd.to_datetime)
# convert string numbers to float
df[df.columns[4:]] = df[df.columns[4:]].astype(float)
df['Month'] = df['start_date'].dt.strftime('%B %Y')
# get the most current data for each state
most_current_df = df.iloc[df.groupby('state')['start_date'].idxmax()]
# group by month and state so we can use it in an animation
grp_df = df.sort_values('start_date').groupby(['Month', 'state'])[['new_cases', 'new_deaths']].sum().reset_index()
grp_df['timestamp'] = pd.to_datetime(grp_df['Month'], format='%B %Y')
grp_df = grp_df.sort_values('timestamp')
grp_df['new_deaths'] = grp_df.groupby('state')['new_deaths'].cumsum()

# create the map
# use below for animation map
# covid_map = px.choropleth(grp_df,
#                           locations='state', locationmode="USA-states", scope="usa",
#                           color='new_cases', color_continuous_scale=px.colors.diverging.RdYlGn_r,
#                           animation_group='state', animation_frame='Month',
#                           labels={'new_cases': 'New Cases', 'state': 'State'})

# create the covid map
covid_map = px.choropleth(most_current_df, locations='state', locationmode="USA-states", scope="usa",
                          color='tot_cases', color_continuous_scale=px.colors.diverging.RdYlGn_r,
                          labels={'tot_cases': 'Total Cases', 'state': 'State'})
covid_map.update_layout(dict(template='plotly_dark',
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)'))

# create the deaths graph
death_fig = px.bar(grp_df[grp_df['Month'].ne('January 2020')].sort_values(['timestamp', 'state']),
                   x='state', y='new_deaths', color='state',
                   animation_frame='Month', title='COVID-19 Deaths',
                   labels={'state': 'State', 'new_deaths': 'Deaths'})
death_fig.update_layout(dict(template='plotly_dark',
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)',
                             showlegend=False),
                        transition={'duration': 1000})

# create the all data graph - i.e., line and bar
all_data = df.groupby('start_date')[df.columns[4:]].sum().reset_index()

all_data_fig = make_subplots(specs=[[{"secondary_y": True}]])

all_data_fig.add_trace(
    go.Scatter(x=all_data['start_date'], y=all_data['tot_cases'],
               name=f'Total Cases', mode='lines', showlegend=False),
    secondary_y=False
)

all_data_fig.add_trace(
    go.Bar(x=all_data['start_date'], y=all_data['new_cases'], name=f'New Cases', showlegend=False),
    secondary_y=True
)

all_data_fig.update_layout(dict(hovermode='x unified', title='COVID-19 Cases', template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)')
                           )
