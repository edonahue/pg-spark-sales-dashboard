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

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = os.getenv('GOOGLE_SHEETS_CREDS_JSON')
print(creds)
#with open('gcreds.json', 'w') as fp:
#    json.dump(json.loads(creds.replace('\n','')), fp)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds.replace('\n','')), scope)
gc = gspread.authorize(credentials)

spreadsheet_key = '1QJ1Kn2j2WpLZbKnci6pyz_XpV7ULCs8qV3mA3cfV1gg'

wks_name = 'sales_totals'
gtotals = g2d.download(gfile=spreadsheet_key, wks_name=wks_name, credentials=credentials, col_names=True)
gtotals['total'] = gtotals.total.astype(float)
gtotals['sold'] = gtotals.sold.astype(float)
gtotals['left'] = gtotals.left.astype(float)
gtotals['sales_revenue'] = gtotals.sales_revenue.astype(float)
# gtotals.head()

gtotals_daily = gtotals[['date', 'total', 'sold', 'left', 'sales_revenue']].groupby('date').max().reset_index()

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(children=[
    html.H1(children='Positive Grid Spark Amplifier Sales Metrics'),
    html.Div([html.P(["Dashboard of sales volume and revenue metrics for the ", html.A("Positive Grid Spark amplifier", href="https://www.positivegrid.com/spark/"), 'based on ', html.A("public API response data.", href="https://api.positivegrid.com/api/counter/spark_preorder_2019")]
    )]),
    html.P("Select y-axis"),
    dcc.Dropdown(
        id='y-axis',
        options=[
            {'label': x.title(), 'value': x} 
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
        gtotals_daily, x="date", y=y, title="Positive Grid Spark daily Sales"
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
