import os
import flask
import dash
from dash import dcc
from dash import html
# import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(external_stylesheets=external_stylesheets, server=server)

app.layout = html.Div([
    html.H2('Hello World'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='display-value')
])

@app.callback(dash.dependencies.Output('display-value', 'children'),
                [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)