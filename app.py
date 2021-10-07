import os
import flask
import dash
from dash import dcc
from dash import html
import pandas as pd
import datetime
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Steve Riesenberg sample project for Smallhold

##################################################################
# load and process data 
##################################################################


def load_data(data_filepath = 'data/', co2_filepath = 'co2.csv', temp_filepath = 'temp.csv', humidity_filepath = 'humidity.csv'):
    co2 = pd.read_csv(data_filepath + co2_filepath, header=None, names=['timestamp', 'value'])
    temp = pd.read_csv(data_filepath + temp_filepath, header=None, names=['timestamp', 'value'])
    humidity = pd.read_csv(data_filepath + humidity_filepath, header=None, names=['timestamp', 'value'])
    return co2, temp, humidity


def process_data(df):
    df['date_time'] = df.timestamp.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))

    # resampling to condense data into 5 minute intervals
    # need the date_time as an index
    df.index = df.date_time
    # take mean of last five minutes
    df = df.resample('300s', label='right')['value'].mean()
    # get the datetime back out of the index
    df = df.reset_index()
    
    df['day'] = df.date_time.apply(lambda x: x.day)
    df['month'] = df.date_time.apply(lambda x: x.month)
    df['year'] = df.date_time.apply(lambda x: x.year)

    # I wanted to do some sort of anomaly detection but ran out of time so opted for this simple approach
    low_outlier = df['value'].mean() - df['value'].std()*3
    high_outlier = df['value'].mean() + df['value'].std()*3
    # would make this a boolean but it looks better in the graph if it's a string
    df['outlier'] = df['value'].apply(lambda x: 'outlier' if x > high_outlier or x < low_outlier else 'normal')

    return df


co2, temp, humidity = load_data()
co2, temp, humidity = process_data(co2), process_data(temp), process_data(humidity)


##################################################################
# templates and colors
##################################################################
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

template = "simple_white"
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
white_button_style = {'background-color': 'white',
                      'color': 'black'}
blue_button_style = {'background-color': 'blue',
                    'color': 'white'}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP, FONT_AWESOME]

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

##################################################################
# initialize dash
##################################################################

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

##################################################################
# making graphs and cards
##################################################################

# function to make the scatter plots, called later in the app layout
def make_time_scatter(df, title, template = "simple_white"):
    fig = px.scatter(df, x='date_time', y="value", template=template, title=title, color='outlier')
    fig.update_layout(
        title_font_color="black",
        title_font_family="Times New Roman",
        title_font_size=24,
        title_x=0.5, 
        showlegend=False
    )
    fig.update_traces(marker=dict(size=4, opacity=0.6),
                  selector=dict(mode='markers'))
    return fig

# function to update the mushroom image green or red depending on the presence of outliers, called later in the app layout
def get_status_image(df):
    is_outlier = df.loc[df['date_time'].idxmax()]['outlier'] == 'outlier'
    if is_outlier:
        return dbc.CardImg(src=app.get_asset_url('red_mushroom.png'), style=card_icon)
    else:
        return dbc.CardImg(src=app.get_asset_url('healthy_mushroom.png'), style=card_icon)

# function to update the status of the farm depending on outliers, called later in the app layout
def get_status_text(*args):
    is_outlier = any([df.loc[df['date_time'].idxmax()]['outlier'] == 'outlier' for df in args]) 
    if is_outlier:
        return html.H3('Current Status: Needs Attention.', style={'textAlign': 'center','color':"red", 'font-size':'24px'})
    else:
        return html.H3('Current Status: Healthy.', style={'textAlign': 'center','color':"green", 'font-size':'24px'})

# function to count the number of outliers
def count_outliers(df):
    return (df['outlier'] == 'outlier').sum()

# function to update text with number of outliers, called later in the app layout
def get_outlier_text(df, id):
    outlier_count = count_outliers(df)
    if outlier_count == 0:
        return html.H5(children=f"{count_outliers(df)}", id=id, className="card-title", style={'font-size':'36px', 'color':'blue', 'textAlign':'center', 'justify':'center' })
    else:
        return html.H5(children=f"{count_outliers(df)}", id=id, className="card-title", style={'font-size':'36px', 'color':'orange', 'textAlign':'center', 'justify':'center' })


# These are the cards at the top of the page with information about CO2, Temperature, and Humidity
# ideally there would be one card template for these three, like I did the scatter plots, but I ran out of time
co2_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("CO2", className="card-title", style={'font-size':'24px'}),
                    html.P(f"The current CO2 value in the farm is {round(co2.loc[co2['date_time'].idxmax()]['value'], 0)} PPM", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            # call the function to get the red or green mushroom as an image
            get_status_image(co2),
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
) 

temp_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Temperature", className="card-title", style={'font-size':'24px'}),
                    html.P(f"The current temperature value in the farm is {round(temp.loc[temp['date_time'].idxmax()]['value'], 1)} degrees", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            # call the function to get the red or green mushroom as an image
            get_status_image(temp),
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
) 

humidity_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Humidity", className="card-title", style={'font-size':'24px'}),
                    html.P(f"The current humidity value in the farm is {round(humidity.loc[humidity['date_time'].idxmax()]['value'], 0)} percent", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            # call the function to get the red or green mushroom as an image
            get_status_image(humidity),
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
)

# These are the cards on the right with information about the number of outliers
co2_outlier_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("CO2", className="card-title", style={'font-size':'24px'}),
                    html.P("Count of times the CO2 in the farm went above or below healthy limits.", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            [html.Br(),
            # call the function to get the formatted text count of the outliers
            get_outlier_text(co2, id='co2_outlier_count')],
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
) 

temp_outlier_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Temp", className="card-title", style={'font-size':'24px'}),
                    html.P("Count of times the temperature in the farm went above or below healthy limits.", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            [html.Br(),
            # call the function to get the formatted text count of the outliers
            get_outlier_text(temp, id='temp_outlier_count')],
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
) 

humidity_outlier_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Humidity", className="card-title", style={'font-size':'24px'}),
                    html.P("Count of times the humidity in the farm went above or below healthy limits.", className="card-text",
                    style={'font-size':'14px'}),
                ]
            )
        ),
        dbc.Card(
            [html.Br(),
            # call the function to get the formatted text count of the outliers
            get_outlier_text(humidity, id='humidity_outlier_count')],
            style={"maxWidth": 100}),
    ],
    className="mt-4 shadow"
) 
##################################################################
# start App
##################################################################

# start declaring the actual app layout 

app.layout = html.Div(children=[
    # Page Title
    html.H1(
        children='Smallhold Mushrooms',
        style={
            'font-size':'80px',
            'textAlign': 'center',
            'color':"black"
        }
    ),
    # Page Sub Title
    html.H2(children='Your mushroom farm at a glance.', 
            style={
        'textAlign': 'center',
        'color':"black",
        'font-size':'32px'
        }
    ),

    html.Br(),
    html.Br(),
    html.Br(),

    # health and incidents
    html.Div(children=[
        html.Div(children=[
                    # get the current status text depending on the latest values
                    get_status_text(co2, temp, humidity),
                    dbc.Row(dbc.Col([co2_card, temp_card, humidity_card], md=10))
                ], 
            style={'display': 'inline-block'}
            ),

        html.Div(children=[
                    # Callback will change this if time is updated
                    html.H3('Incidents in last 24 hours.', id='incidents_count_text', style={'textAlign': 'center','color':"black", 'font-size':'20px'}),
                    dbc.Row(dbc.Col([co2_outlier_card, temp_outlier_card, humidity_outlier_card], md=10))
                ], 
            style={'display': 'inline-block'}
            )
        ],
        style = {'textAlign':'center'}
    ),

    html.Br(),
    html.Br(),

    html.H3(children='Detailed sensor data.', 
            style={
        'textAlign': 'center',
        'color':"black",
        'font-size':'24px'
        }
    ),
    # Buttons
    html.Div(children = [
                html.P('Show me data for the last: ', style={'color': 'black', 'fontSize': 14}),
                html.Button('24 Hours', id='btn-24-Hours', n_clicks=0, style=blue_button_style),
                html.Button('3 Days', id='btn-3-Days', n_clicks=0, style=white_button_style),
                html.Button('1 Week', id='btn-1-Week', n_clicks=0, style=white_button_style),
                html.Button('All Time', id='btn-All-Time', n_clicks=0, style=white_button_style)
                ],
                style={'textAlign':'center'}
            ),
    # Graphs
    html.Div(children = [
        dcc.Graph(
            # these aren't initialized but are set in the else statement of the button callback
            id='co2-graph', 
            style={'display': 'inline-block', 'width':625}
            ), 
        dcc.Graph(
            id='temp-graph', 
            style={'display': 'inline-block', 'width':625}
            ),
        dcc.Graph(
            id='humidity-graph',
            style={'display': 'inline-block', 'width':625}
            )
    ], 
        style={'width': '100%', 'display': 'inline-block'})
])

##############################################################
# Start Interactive Callbacks
##############################################################


# Graph Creation and Filtering from Buttons
@app.callback(Output('co2-graph', 'figure'),
            Output('temp-graph', 'figure'),
            Output('humidity-graph', 'figure'),
            Input('btn-24-Hours', 'n_clicks'),
            Input('btn-3-Days', 'n_clicks'),
            Input('btn-1-Week', 'n_clicks'), 
            Input('btn-All-Time', 'n_clicks'))
def update_figure(btn1, btn2, btn3, btn4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    data_list = {'co2':co2, 'temp':temp, 'humidity':humidity}
    # generate max dates
    max_date_dict = {dfname:df['date_time'].max() for dfname, df in data_list.items()}
    # subtract button time from max date and store in a dict for each data set
    if 'btn-24-Hours' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
    elif 'btn-3-Days' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=3) for dfname, df in data_list.items()}
    elif 'btn-1-Week' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=7) for dfname, df in data_list.items()}
    elif 'btn-All-Time' in changed_id:
        min_date_dict = {dfname:df['date_time'].min() for dfname, df in data_list.items()}
    else:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
    
    # filter between min and max date
    co2_button_filter = (co2['date_time'] <= max_date_dict['co2']) & (co2['date_time'] >= min_date_dict['co2'])
    temp_button_filter = (temp['date_time'] <= max_date_dict['temp']) & (temp['date_time'] >= min_date_dict['temp'])
    humidity_button_filter = (humidity['date_time'] <= max_date_dict['humidity']) & (humidity['date_time'] >= min_date_dict['humidity'])

    # filter data frames
    co2_filtered = co2[co2_button_filter]
    temp_filtered = temp[temp_button_filter]
    humidity_filtered = humidity[humidity_button_filter]

    # make figures
    co2_fig = make_time_scatter(co2_filtered, title='<b>CO2 PPM</b>')
    temp_fig = make_time_scatter(temp_filtered, title='<b>Temperature in Degrees Fahrenheit</b>')
    humidity_fig = make_time_scatter(humidity_filtered, title='<b>Humidity Percentage</b>')
    co2_fig.update_layout(transition_duration=500)
    temp_fig.update_layout(transition_duration=500)
    humidity_fig.update_layout(transition_duration=500)

    return co2_fig, temp_fig, humidity_fig

# Button Styling -- turns the button blue when it's clicked
@app.callback(Output('btn-24-Hours', 'style'),
    Output('btn-3-Days', 'style'),
    Output('btn-1-Week', 'style'),
    Output('btn-All-Time', 'style'),
    Input('btn-24-Hours', 'n_clicks'),
    Input('btn-3-Days', 'n_clicks'),
    Input('btn-1-Week', 'n_clicks'), 
    Input('btn-All-Time', 'n_clicks'))
def change_button_style(btn1, btn2, btn3, btn4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    style_24, style3, style1, styleall = white_button_style, white_button_style, white_button_style, white_button_style
    if 'btn-24-Hours' in changed_id:
        style_24 = blue_button_style
    elif 'btn-3-Days' in changed_id:
        style3 = blue_button_style
    elif 'btn-1-Week' in changed_id:
        style1 = blue_button_style
    elif 'btn-All-Time' in changed_id:
        styleall = blue_button_style
    else:
        style_24 = blue_button_style
    return style_24, style3, style1, styleall


# Update outlier counts from Buttons
@app.callback(Output('co2_outlier_count', 'children'),
            Output('temp_outlier_count', 'children'),
            Output('humidity_outlier_count', 'children'),
            Output('incidents_count_text', 'children'),
            Input('btn-24-Hours', 'n_clicks'),
            Input('btn-3-Days', 'n_clicks'),
            Input('btn-1-Week', 'n_clicks'), 
            Input('btn-All-Time', 'n_clicks'))
def update_outlier_count(btn1, btn2, btn3, btn4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    data_list = {'co2':co2, 'temp':temp, 'humidity':humidity}
    # generate max dates
    max_date_dict = {dfname:df['date_time'].max() for dfname, df in data_list.items()}
    # subtract button time from max date and store in a dict for each data set
    if 'btn-24-Hours' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
        incidents_count_text = 'Incidents in last 24 Hours'
    elif 'btn-3-Days' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=3) for dfname, df in data_list.items()}
        incidents_count_text = 'Incidents in last 3 Days'
    elif 'btn-1-Week' in changed_id:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=7) for dfname, df in data_list.items()}
        incidents_count_text = 'Incidents in last 1 Week'
    elif 'btn-All-Time' in changed_id:
        min_date_dict = {dfname:df['date_time'].min() for dfname, df in data_list.items()}
        incidents_count_text = 'Incidents All Time'
    else:
        min_date_dict = {dfname:max_date_dict[dfname] - datetime.timedelta(days=1) for dfname, df in data_list.items()}
        incidents_count_text = 'Incidents in last 24 Hours'
    
    # filter between min and max date
    co2_button_filter = (co2['date_time'] <= max_date_dict['co2']) & (co2['date_time'] >= min_date_dict['co2'])
    temp_button_filter = (temp['date_time'] <= max_date_dict['temp']) & (temp['date_time'] >= min_date_dict['temp'])
    humidity_button_filter = (humidity['date_time'] <= max_date_dict['humidity']) & (humidity['date_time'] >= min_date_dict['humidity'])

    # filter data frames
    co2_filtered = co2[co2_button_filter]
    temp_filtered = temp[temp_button_filter]
    humidity_filtered = humidity[humidity_button_filter]

    # make counts
    co2_outlier_count = get_outlier_text(co2_filtered, id='co2_outlier_count')
    temp_outlier_count = get_outlier_text(temp_filtered, id='temp_outlier_count')
    humidity_outlier_count = get_outlier_text(humidity_filtered, id='humidity_outlier_count')

    return co2_outlier_count, temp_outlier_count, humidity_outlier_count, incidents_count_text


if __name__ == '__main__':
    app.run_server(debug=True)