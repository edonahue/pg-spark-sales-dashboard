import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import os
import json
import gspread
from df2gspread import df2gspread as d2g
from df2gspread import gspread2df as g2d
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'google-credentials.json', scope)
gc = gspread.authorize(credentials)

spreadsheet_key = '1QJ1Kn2j2WpLZbKnci6pyz_XpV7ULCs8qV3mA3cfV1gg'

wks_name = 'sales_totals'
gtotals = g2d.download(gfile=spreadsheet_key, wks_name=wks_name, credentials=credentials, col_names=True)
gtotals['total'] = gtotals.total.astype(int)
gtotals['sold'] = gtotals.sold.astype(int)
gtotals['left'] = gtotals.left.astype(int)
gtotals['sales_revenue'] = gtotals.sales_revenue.astype(int)
# gtotals.head()

gtotals_daily = gtotals[['date', 'total', 'sold', 'left', 'sales_revenue']].groupby('date').sum().reset_index()

app = dash.Dash(__name__)
app.layout = html.Div([
    html.P("Select y-axis"),
    dcc.Dropdown(
        id='y-axis',
        options=[
            {'label': x, 'value': x} 
            for x in ['total', 'sales_revenue']],
        value='total'
    ),
    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"), 
    [Input("y-axis", "value")])
def display_area(y):
    fig = px.area(
        gtotals_daily, x="date", y=y
    )
    return fig

app.run_server(debug=True)


