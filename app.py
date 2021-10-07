import os
import flask
import dash
from dash import dcc
from dash import html
import pandas as pd
import datetime
import plotly.express as px
from dash.dependencies import Input, Output


##################################################################
# load data 
##################################################################

def load_data(data_filepath = 'data/', co2_filepath = 'co2.csv', temp_filepath = 'temp.csv', humidity_filepath = 'humidity.csv'):
    co2 = pd.read_csv(data_filepath + co2_filepath, header=None, names=['timestamp', 'value'])
    temp = pd.read_csv(data_filepath + temp_filepath, header=None, names=['timestamp', 'value'])
    humidity = pd.read_csv(data_filepath + humidity_filepath, header=None, names=['timestamp', 'value'])
    return co2, temp, humidity
def process_data(df):
    df['date_time'] = df.timestamp.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
    df['day'] = df.date_time.apply(lambda x: x.day)
    df['month'] = df.date_time.apply(lambda x: x.month)
    df['year'] = df.date_time.apply(lambda x: x.year)
    return df

co2, temp, humidity = load_data()
co2, temp, humidity = process_data(co2), process_data(temp), process_data(humidity)


##################################################################
# templates and colors
##################################################################

template = "simple_white"
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
white_button_style = {'background-color': 'white',
                      'color': 'black'}
blue_button_style = {'background-color': 'blue',
                    'color': 'white'}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

##################################################################
# making graphs
##################################################################

def make_time_scatter(df, title, template = "simple_white"):
    fig = px.scatter(df, x='date_time', y="value", template=template, title=title)
    fig.update_layout(
        title_font_color="black",
        title_font_family="Times New Roman",
        title_font_size=24,
        title_x=0.5
    )
    fig.update_traces(marker=dict(size=4, opacity=0.6),
                  selector=dict(mode='markers'))
    return fig


co2_fig = make_time_scatter(co2, title='<b>CO2 PPM</b>')
temp_fig = make_time_scatter(temp, title='<b>Temperature in Degrees Fahrenheit</b>')
humidity_fig = make_time_scatter(humidity, title='<b>Humidity Percentage</b>')

# temp_fig.update_layout(
#     title_font_color="blue",
#     title_font_family="Times New Roman",
#     title_x=0.5, 
#     xaxis_range = [temp.date_time.min(), temp.date_time.max()]
# )


# temp_fig.update_xaxes(
#     rangeslider_visible=True,
#     rangeselector=dict(
#         buttons=list([dict(count=24, label="24 HRS", step="hour", stepmode="backward"),
#             dict(count=3, label="3 Days", step="day", stepmode="todate"),
#             dict(count=7, label="1 week", step="day", stepmode="backward"),
#             dict(step="all")
#         ])
#     )
# )

##################################################################
# start App
##################################################################

server = flask.Flask(__name__)
app = dash.Dash(external_stylesheets=external_stylesheets, server=server)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# server = app.server

app.layout = html.Div(children=[
    # Page Title
    html.H1(
        children='Smallhold Farm',
        style={
            'textAlign': 'center',
            'color':"black"
        }
    ),
    # Page Sub Title
    html.H3(children='A look at the farm.', 
            style={
        'textAlign': 'center',
        'color':"black"
        }
    ),


    html.Div(children = [
                html.P('Show me data for the last: ', style={'color': 'black', 'fontSize': 14}),
                html.Button('24 Hours', id='btn-24-Hours', n_clicks=0, style=blue_button_style),
                html.Button('3 Days', id='btn-3-Days', n_clicks=0, style=white_button_style),
                html.Button('1 Week', id='btn-1-Week', n_clicks=0, style=white_button_style),
                html.Button('All Time', id='btn-All-Time', n_clicks=0, style=white_button_style)
                ],
                style={'textAlign':'center'}
            ),
    html.Div(children = [
    # dcc.Slider(
    #     id='date-slider',
    #     min=temp['day'].min(),
    #     max=temp['day'].max(),
    #     # value=temp['date_time'].max() - datetime.timedelta(days=1),
    #     # marks={f'2021/9/{day}': f'2021/9/{day}' for day in temp['day'].unique()},
    #     marks={str(day): str(day) for day in temp['day'].unique()}
    #     # step=None
    # ),
        dcc.Graph(
            id='co2-graph', figure=co2_fig, style={'display': 'inline-block', 'width':625}
            ), 
        dcc.Graph(
            id='temp-graph',  figure=temp_fig,
            style={'display': 'inline-block', 'width':625}
            ),
        dcc.Graph(
            id='humidity-graph', figure=humidity_fig,
            style={'display': 'inline-block', 'width':625}
            )
    ], 
        style={'width': '100%', 'display': 'inline-block'})
])

# @app.callback(Output('co2-graph', 'figure'),
#             Output('temp-graph', 'figure'),
#             Output('humidity-graph', 'figure'),
#             Input('btn-24-Hours', 'n_clicks'),
#             Input('btn-3-Days', 'n_clicks'),
#             Input('btn-1-Week', 'n_clicks'), 
#             Input('btn-All-Time', 'n_clicks'))
# def update_figure(btn1, btn2, btn3, btn4):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     data_list = {'co2':co2, 'temp':temp, 'humidity':humidity}
#     max_date_dict = {dfname:df['date_time'].max() for dfname, df in data_list.items()}
#     if 'btn-24-Hours' in changed_id:
#         min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
#     elif 'btn-3-Days' in changed_id:
#         min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=3) for dfname, df in data_list.items()}
#     elif 'btn-1-Week' in changed_id:
#         min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=7) for dfname, df in data_list.items()}
#     elif 'btn-All-Time' in changed_id:
#         min_date_dict = {dfname:df['date_time'].min() for dfname, df in data_list.items()}
#     else:
#         min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
    
#     co2_button_filter = (co2['date_time'] <= max_date_dict['co2']) & (co2['date_time'] >= min_date_dict['co2'])
#     temp_button_filter = (temp['date_time'] <= max_date_dict['temp']) & (temp['date_time'] >= min_date_dict['temp'])
#     humidity_button_filter = (humidity['date_time'] <= max_date_dict['humidity']) & (humidity['date_time'] >= min_date_dict['humidity'])
#     co2_filtered = co2[co2_button_filter]
#     temp_filtered = temp[temp_button_filter]
#     humidity_filtered = humidity[humidity_button_filter]
#     co2_fig = make_time_scatter(co2_filtered, title='<b>CO2 PPM</b>')
#     temp_fig = make_time_scatter(temp_filtered, title='<b>Temperature in Degrees Fahrenheit</b>')
#     humidity_fig = make_time_scatter(humidity_filtered, title='<b>Humidity Percentage</b>')
#     # co2_fig.update_layout(transition_duration=500)
#     # temp_fig.update_layout(transition_duration=500)
#     # humidity_fig.update_layout(transition_duration=500)

#     return co2_fig, temp_fig, humidity_fig

# @app.callback(Output('btn-24-Hours', 'style'),
#     Output('btn-3-Days', 'style'),
#     Output('btn-1-Week', 'style'),
#     Output('btn-All-Time', 'style'),
#     Input('btn-24-Hours', 'n_clicks'),
#     Input('btn-3-Days', 'n_clicks'),
#     Input('btn-1-Week', 'n_clicks'), 
#     Input('btn-All-Time', 'n_clicks'))
# def change_button_style(btn1, btn2, btn3, btn4):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     style_24, style3, style1, styleall = white_button_style, white_button_style, white_button_style, white_button_style
#     if 'btn-24-Hours' in changed_id:
#         style_24 = blue_button_style
#     elif 'btn-3-Days' in changed_id:
#         style3 = blue_button_style
#     elif 'btn-1-Week' in changed_id:
#         style1 = blue_button_style
#     elif 'btn-All-Time' in changed_id:
#         styleall = blue_button_style
#     else:
#         style_24 = blue_button_style
#     return style_24, style3, style1, styleall

if __name__ == '__main__':
    app.run_server(debug=True)