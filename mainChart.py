import webbrowser
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import graph
import colorsChart as bar_graph
import general_pie_chart
import graphPerAge as line_chart

def load_data(file_path):
    return pd.read_excel(file_path, engine='openpyxl')

def calculate_metrics(df):
    total_people = df.iloc[0, 0]
    avg_people = df.iloc[0, 1]
    max_people_hour = df.iloc[0, 2]
    return total_people, avg_people, max_people_hour

df = load_data('static/excelsFiles/excelLoadsPerHours.xlsx')
column_names = df.columns[1:]
bar_df = load_data('static/excelsFiles/excelLoadsColors.xlsx')
count_people_df = load_data('static/excelsFiles/excelCountPeople.xlsx')
general_pie_df = load_data('static/excelsFiles/excelCountGenerally.xlsx')

total_people, avg_people, max_people_hour = calculate_metrics(count_people_df)

def create_layout():
    return html.Div(
        className='main-container',
        children=[
            html.Div(
                className='header-container',
                children=[
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('# of Visitors', className='metric-title'),
                            html.Div(f'{total_people:.1f}k', className='metric-value')
                        ]
                    ),
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('Avg Duration People', className='metric-title'),
                            html.Div(f'{avg_people:.2f}', className='metric-value')
                        ]
                    ),
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('Max Visitors/Hour', className='metric-title'),
                            html.Div(f'{max_people_hour:.1f}k', className='metric-value')
                        ]
                    ),
                ]
            ),
            html.Div(
                className='charts-container',
                children=[
                    dcc.Graph(id='pie-selection', className='pie-chart'),
                    dcc.Graph(id='bar-chart', className='bar-chart'),
                    dcc.Graph(id='general-pie-chart', className='general-pie-chart'),
                ]
            ),
            html.Div(
                className='bottom-charts-container',
                children=[
                    dcc.Graph(id='line-chart', figure=line_chart.create_line_chart(), className='line-chart'),
                    html.Div(html.Img(src='/assets/defaultImage.jpg', className='image'), className='image-container'),
                ]
            )
        ]
    )

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/')

app.layout = create_layout()

@app.callback(
    [Output('pie-selection', 'figure'),
     Output('bar-chart', 'figure'),
     Output('general-pie-chart', 'figure')],
    [Input('pie-selection', 'clickData')]
)
def update_graphs(clickData):
    selected_categories = column_names.tolist()
    if clickData:
        selected_categories = [clickData['points'][0]['label']]

    pie_fig = graph.create_graph(selected_categories)
    bar_fig = bar_graph.create_bar_chart(bar_df)
    general_pie_fig = general_pie_chart.create_general_pie_chart(general_pie_df)
    return pie_fig, bar_fig, general_pie_fig

if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True)
