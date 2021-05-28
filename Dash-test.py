import numpy as np
import pandas as pd
import dash
from datetime import datetime, timedelta
#import plotly.express as px
#import dash_table
#from plotly.graph_objs import *
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
#from geopy.geocoders import Nominatim
#from geopy.extra.rate_limiter import RateLimiter
#from plotly.subplots import make_subplots

df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv', delimiter = ",", encoding="utf-8-sig")
df.to_csv('test.csv')
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR],
            meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
server = app.server

df['date'] = pd.to_datetime(df['date'],errors='ignore')
df['iso_code'] = df['iso_code'].astype('str')
df['continent'] = df['continent'].astype('str')
df['location'] = df['location'].astype('str')
#df['tota_tests'] = df['total_tests'].astype('int')
#df['total_deaths'] = df['total_deaths'].astype('Int32')
df['total_deaths'].fillna(0,inplace=True)
df['total_cases'].fillna(0,inplace=True)
df['total_tests'].fillna(0,inplace=True)


df.drop(df[(df['iso_code']=='OWID_WRL')].index, inplace=True)
df.dropna(thresh=23, inplace=True)

continent_df = df.groupby(['location','date']).agg({'population':'mean','new_tests':'sum'}).reset_index()

continent_df['percentage_covered'] = (continent_df['new_tests']/continent_df['population'])*100
#print(df.tail)
#continent_df.to_csv('test.csv')

#Table
max_date = df['date'].max()


new_cases_df = df.groupby('date',as_index=False)[['new_cases','new_tests','total_cases','total_tests']].sum()

second_max_date = max_date-timedelta(1)
table_df = continent_df[(continent_df['date']==second_max_date)]
#table_df = continent_df.copy()
table_df.population = table_df.population.round(2)
table_df.total_tests = table_df.new_tests.round(2)
table_df.percentage_covered = table_df.percentage_covered.round(2)

#print(table_df)

#new_cases_df.to_csv('test.csv')

date = df['date'].max() - timedelta(1)
total_cases = int(sum(df[df['date'] == date]['total_cases']))
total_deaths = int(sum(df[df['date'] == date]['total_deaths']))
#total_tests = (sum(df[df['date'] == date]['total_tests'])
total_tests = sum(new_cases_df['new_tests'])
#print(date)
countries_affected = len(pd.unique(df['location']))
#active_cases = total_cases-total_deaths


#latitude=[]
#longitude=[]

'''def find_location(location):
    
    geolocator=Nominatim(user_agent="Dash-test")
    return geolocator.geocode(location)

for code in df['iso_code']:
     if find_location(code)!=None:
         loc = find_location(code)
         latitude.append(loc.latitude)
         longitude.append(loc.longitude)
     else:
        latitude.append(np.nan) 
        longitude.append(np.nan)

df["Longitude"] = longitude 
df["Latitude"] = latitude'''

# Functions for all the graphs

def draw_map():
    map_cases = go.Figure(data=go.Choropleth(
        locations = df['iso_code'],
        z = df['total_cases'],
        hovertext=None,
        colorscale = 'viridis', 
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        #colorbar_tickprefix = '$',
        colorbar_title = 'Total Cases',
        colorbar=dict(tickcolor='white')
      )
    )

    map_cases.update_layout(
        title_text='Covid 19 cases Worldwide',
        title_x = 0.3,
        title_y = 0.9,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)'
            ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgb(1,53,66)',
        margin=dict(r=30, t=30, l=40, b=40),
        font=dict(color="lightseagreen")
    )
     
    #return map_cases
    return dcc.Graph(id='world-cases-map',figure=map_cases)


def draw_totcases_card():
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6("Total Cases", className="card-title"),
                html.H4(total_cases, className="card-subtitle",style={'color':'darkorange'}),
            ]
        ),
        color="rgb(1,53,66)", inverse=True, style={"width": "11rem","height": "5rem"}
    )
    return(card)

def draw_totdeaths_card():
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6("Total Deaths", className="card-title"),
                html.H4(total_deaths, className="card-subtitle",style={'color':'red'})
                ],id='total-deaths'
        ),
        color="rgb(1,53,66)", inverse=True, style={"width": "11rem","height": "5rem"}
    )
    return(card)

def draw_actcases_card():
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6("Total Tests", className="card-title"),
                html.H4(total_tests, className="card-subtitle",style={'color':'slategrey'})
                ],id='active-cases'
        ),
        color="rgb(1,53,66)", inverse=True, style={"width": "11rem","height": "5rem"}
    )
    return(card)

def draw_contries_card():
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6("Countries affected", className="card-title"),
                html.H4(countries_affected, className="card-subtitle",style={'color':'#CDBA1F'})
                ],id='countries-affected'
        ),
        color="rgb(1,53,66)", inverse=True, style={"width": "12rem","height": "5rem"}
    )
    return(card)
#Test cases stacked bar
def draw_new_trend():
    new_trend_graph = go.Figure(data=[go.Bar(name='Daily new cases', x=new_cases_df['date'],y=new_cases_df['new_cases'],hovertemplate= "Date: %{x}<br>New Cases: %{y}",marker_color='darkorange'),
                      go.Bar(name='New Tests taken daily', x=new_cases_df['date'],y=new_cases_df['new_tests'],hovertemplate= "Date: %{x}<br>New Tests: %{y}",marker_color='lightblue')])
    new_trend_graph.update_layout(
        title={'text':'New tests vs New cases',
               'y':0.9,
               'x':0.55,
               'xanchor':'center',
               'yanchor':'top'},
        barmode='stack',legend=dict(yanchor="top",xanchor="left",y=1.1,x=0),
        margin=dict(l=10,r=10,b=20,t=10),height=275,width=600,
        yaxis=dict(
        tickmode='array',
        tickvals=[0, 2000000,4000000,6000000,8000000],
        ticktext=['0','2M','4M','6M','8M'],
        gridwidth=0.001,
        gridcolor='darkgrey',
        color='grey'
        ),
        xaxis=dict(color='grey'),
        plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgb(1,53,66)',
        font=dict(color="lightseagreen"))
    new_trend_graph.show()
    return dcc.Graph(id='new-trend-graph',figure=new_trend_graph)
        

def draw_total_trend():
    total_trend_graph = go.Figure(data=[go.Bar(name='Total cases', x=new_cases_df['date'],y=new_cases_df['total_cases'],hovertemplate= "Date: %{x}<br>Total Cases: %{y}",marker_color='darkorange'),
                      go.Bar(name='Total Tests taken', x=new_cases_df['date'],y=new_cases_df['total_tests'],hovertemplate= "Date: %{x}<br>Total Tests: %{y}",marker_color='lightblue')])
    total_trend_graph.update_layout(
        title={'text':'Total tests vs Total cases',
               'y':0.9,
               'x':0.55,
               'xanchor':'center',
               'yanchor':'top'},
        barmode='stack',legend=dict(yanchor="top",xanchor="left",y=1.3,x=0,bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=10,r=10,b=20,t=10),height=275,width=600,
        yaxis=dict(
        tickmode='array',
        #tickvals=[0, 80000000,160000000,240000000],
        #ticktext=['0','80M','160M','240M'],
        gridwidth=0.001,
        gridcolor='darkgrey',
        color='grey'),
        xaxis=dict(color='grey'),
        plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgb(1,53,66)',
        font=dict(color="lightseagreen"))
    total_trend_graph.show()
    
    return dcc.Graph(id='total-trend-graph',figure=total_trend_graph)
        


def draw_table():
    headerColor = 'black'
    rowEvenColor = 'grey'
    rowOddColor = 'darkgrey'
    table_fig = go.Figure(data=[go.Table(
    header=dict(values=['Country', 'Population', 'Total tests','Percentage covered'],
                fill_color=headerColor,
                align=['left','center'],
                line_color='lightgrey',
                font=dict(color='white',size=12)),
    cells=dict(values=[table_df.location, table_df.population, table_df.total_tests,
                       table_df.percentage_covered],
               line_color='lightgrey',
               fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*202],
               align=['left','center'],
               font=dict(color='black',size=11)))])
    table_fig.update_layout(title={'text':'% of population covered in tests',
                'x':0.5,
                'y':0.97,
               'xanchor':'center',
               'yanchor':'middle',},
                height=600, width=630, font=dict(color='lightseagreen'), margin=dict(l=30,r=30,b=30,t=30),paper_bgcolor='rgb(1,53,66)')
    #table_fig.show()
    
        
    '''return dash_table.DataTable(id='table',
    style_cell={
        'whiteSpace': 'normal',
        'height': '3px',
        'width':'120px',
    },
    page_size=12,
    columns=[{"name": i, "id": i} for i in table_df.columns],
    data=table_df.to_dict('records'),
    )'''
    return dcc.Graph(id='table',figure=table_fig)


#Top 10 countries trend calculation
top_cases_df = pd.DataFrame({'countries':df.groupby('location')['total_cases'].max().nlargest(10).index.get_level_values('location'),
                     'count':df.groupby('location')['total_cases'].max().nlargest(10)}).reset_index()

top_deaths_df = pd.DataFrame({'countries':df.groupby('location')['total_deaths'].max().nlargest(10).index.get_level_values('location'),
                     'count':df.groupby('location')['total_deaths'].max().nlargest(10)}).reset_index()

top_onedayspike_cases_df = pd.DataFrame({'countries':df.groupby('location')['new_cases'].max().nlargest(10).index.get_level_values('location'),
                     'count':df.groupby('location')['new_cases'].max().nlargest(10)}).reset_index()

top_onedayspike_deaths_df = pd.DataFrame({'countries':df.groupby('location')['new_deaths'].max().nlargest(10).index.get_level_values('location'),
                     'count':df.groupby('location')['new_deaths'].max().nlargest(10)}).reset_index()


def display_cases(locationname,cases):
    return html.P([html.Span(locationname + ' | ' + str(int(cases)))
                   ],style={'textAlign': 'center','color': 'rgb(200,200,200)','fontsize':14,
                })
    
top_cases_list = []
top_deaths_list = []
top_onedayspike_cases_list = []
top_onedayspike_deaths_list = []


[top_cases_list.append(display_cases(top_cases_df.iloc[itr,1],top_cases_df.iloc[itr,2])) for itr in range(1, 10)]

[top_deaths_list.append(display_cases(top_deaths_df.iloc[itr,1],top_deaths_df.iloc[itr,2])) for itr in range(1, 10)]
    
[top_onedayspike_cases_list.append(display_cases(top_onedayspike_cases_df.iloc[itr,1],top_onedayspike_cases_df.iloc[itr,2])) for itr in range(1, 10)]
    
[top_onedayspike_deaths_list.append(display_cases(top_onedayspike_deaths_df.iloc[itr,1],top_onedayspike_deaths_df.iloc[itr,2])) for itr in range(1, 10)]

# Style for top 10 countries trend
style={
    'margin-left':'20px'
}
column_style={
    'width':'22%',
    'padding':'20',
    'margin-left':'22px',
    'backgroundColor':'rgb(1,53,66)'
}
column_style_2={
    'width':'22%',
    'padding':'25',
    'margin-left':'45px',
    'backgroundColor':'rgb(1,53,66)'
}

right_column_style={
    'width':'22%',
    'padding':'20',
    'margin-left':'40px',
    'backgroundColor':'rgb(1,53,66)'
}

corner_column_style={
    'width':'22%',
    'padding':'20',
    'margin-left':'20px',
    'backgroundColor':'rgb(1,53,66)'
}

tab_styles={
   'height':'40px',
   'width':'600px'
}

tab_style={
   'backgroundColor':'#013542',
   'border':'white',    
   'padding':'4px'
}

selected_tab_style={
    'backgroundColor':'#08ADB1',
    'border':'#08ADB1',
    'color':'white',
    'padding':'4px',
    'fontWeight':'bold'
}

app.layout = html.Div([
    html.Div(children=[
    html.H4('Global covid 19 cases'),
    html.P(children=["December 2019 - Present"],
    style={'margin-top':'-9px','font-size':'15px','font-weight':'normal'})],
        style={
    'textAlign': 'center',
    "background": "#08ADB1",
    'color':'white',
    'fontWeight':'bold'}),
    #html.P(children="december 2019-present"),
        dbc.Row([
            dbc.Col(draw_totcases_card(),width={"offset":0.1}),
            dbc.Col(draw_totdeaths_card(),width={"offset":0.1}),
            dbc.Col(draw_actcases_card(),width={"offset":0.1}),
            dbc.Col(draw_contries_card(),width={"offset":0.1})
            ],no_gutters=True,justify="around"),
    html.Br(),
    html.Br(),
    html.Div(className='row', children=[html.Div(draw_map(), className='col s12 m6 l6',style={'margin-left':'8px'}),
        html.Div(children=[
            dcc.Tabs([
                dcc.Tab(label='New Cases',children=[
                    html.Div(children=[
                    dcc.Dropdown(id='New-cases-dropdown',
                    options=[{'label':itr, 'value':itr} for itr in list(df['location'].unique())],
                    value='India',
                    multi=False,
                    style=dict(width='150px')),
                    html.H6("Select a location to view the daily trend of covid cases",style={'margin-left':'2rem','maring-top':'2rem','color':'lightseagreen'})],
                    style={'display':'flex'},className='col s12 m6 l6'),
                    dcc.Graph(id='New-cases-graph')
                    ],style=tab_style,selected_style=selected_tab_style),
                dcc.Tab(label='New Deaths',children=[
                    html.Div(children=[
                    dcc.Dropdown(id='New-deaths-dropdown',
                    options=[{'label':itr, 'value':itr} for itr in list(df['location'].unique())],
                    value='India',
                    multi=False,
                    style=dict(width='150px')),
                    html.H6("Select a location to view the daily trend of covid deaths",style={'margin-left':'2rem','maring-top':'2rem','color':'lightseagreen'})],
                    style={'display':'flex'},className='col s12 m6 l6'),
                    dcc.Graph(id='New-deaths-graph')
                    ],style=tab_style,selected_style=selected_tab_style)
            ],style=tab_styles),
            ],className='col s12 m6 l6',style={'padding':'0px'}
            )]
    ),
    html.Br(),
    html.Br(),
    html.Div(className='row',children=[html.Div(draw_table(),className='col s12 m12 l12',style={'margin-left':'5px'}),
            html.Div(children=[html.Div(draw_total_trend()),html.Br(),html.Br(),
            html.Div(draw_new_trend())],className='col s12 m6 l6')]
        ),
    html.Br(),
    html.Br(),
    html.Div(className='row',children=[
    html.Div([
        html.P([html.Span('Countries with highest cases: ',
                             ),
                    html.Br(),
        ],style={'textAlign': 'center','color': 'rgb(200,200,200)','fontsize':12,'backgroundColor':'#3B5998','fontSize': 17}),
                html.P(top_cases_list)
    ],style=column_style,id='top-10-cases'),
    html.Div([
        html.P([html.Span('Countries with highest single-day spike in cases: ',
                             ),
                    html.Br(),
        ],style={'textAlign': 'center','color': 'rgb(200,200,200)','fontsize':12,'backgroundColor':'#3B5998','fontSize': 17}),
                html.P(top_onedayspike_cases_list)
    ],style=column_style_2,id='top-spike-cases'),
    html.Div([
        html.P([html.Span('Countries with highest Deaths: ',
                             ),
                    html.Br(),
        ],style={'textAlign': 'center','color': 'rgb(200,200,200)','fontsize':12,'backgroundColor':'#ab2c1a','fontSize': 17}),
                html.P(top_deaths_list)
    ],style=right_column_style,id='top-10-deaths'),
    html.Div([
        html.P([html.Span('Countries with highest single-day spike in deaths: ',
                             ),
                    html.Br(),
        ],style={'textAlign': 'center','color': 'rgb(200,200,200)','fontsize':12,'backgroundColor':'#ab2c1a','fontSize': 17}),
                html.P(top_onedayspike_deaths_list)
    ],style=corner_column_style,id='top-spike-deaths')]
),
    
    # Update each and every component of the dashboard every 24 hours to get
    #latest updates
    dcc.Interval(
        id='world-cases-map-interval',
        interval=86400000),

    dcc.Interval(
        id='total-cases-interval',
        interval=86400000),

])

#callback for drowpdown
@app.callback(
    dash.dependencies.Output('New-cases-graph', 'figure'),
    dash.dependencies.Input('New-cases-dropdown', 'value'))
def draw_new_cases_trend(value):
    location_df = df[df['location']==value]
    trend_graph=go.Figure()
    trend_graph.add_trace(go.Scatter(x=location_df['date'],y=location_df['new_cases'],mode='lines',line_color='darkorange'))
    trend_graph.update_layout(autosize=False,width=600,height=375,plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgb(1,53,66)',
        xaxis=dict(showgrid=False,color='grey',zeroline=False),
        yaxis=dict(showgrid=True,color='grey',gridwidth=0.001,gridcolor='darkgrey',zerolinecolor='darkgrey'),
        margin=dict(l=10,r=10,b=10,t=10))
    return trend_graph

@app.callback(
    dash.dependencies.Output('New-deaths-graph', 'figure'),
    dash.dependencies.Input('New-deaths-dropdown', 'value'))
def draw_new_deaths_trend(value):
    location_df = df[df['location']==value]
    trend_graph=go.Figure()
    trend_graph.add_trace(go.Scatter(x=location_df['date'],y=location_df['new_deaths'],mode='lines',line_color='rgb(217,83,79)'))
    trend_graph.update_layout(autosize=False,width=600,height=375,plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgb(1,53,66)',
        xaxis=dict(showgrid=False,color='grey',zeroline=False),
        yaxis=dict(showgrid=True,color='grey',gridwidth=0.001,gridcolor='darkgrey',zerolinecolor='darkgrey'),margin=dict(l=10,r=10,b=10,t=10))
    return trend_graph

if __name__ == '__main__':
    app.run_server(debug=False)
