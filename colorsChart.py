import pandas as pd
import plotly.graph_objs as go

def create_bar_chart(df):
    faceCaptured = df.columns[0]
    categories = df.columns[1:]

    data = []
    for category in categories:
        trace = go.Bar(
            x=df[faceCaptured],
            y=df[category],
            name=category
        )
        data.append(trace)

    layout = go.Layout(
        barmode='stack',
        annotations=[
            dict(
                text="Quantity by captured faces",  # הטקסט שיופיע בתוך הגרף
                x=1,  # מיקום אופקי של הטקסט (צד ימין)
                y=18,  # מיקום אנכי של הטקסט (צד תחתון)
                font=dict(size=15, color='white'),  # גודל וצבע הפונט
                showarrow=False  # ללא חץ מצביע
            )
        ],
        paper_bgcolor='#34495e',  # Set plot background color
        margin=dict(
            l=5,  # גבול שמאלי
            r=5,  # גבול ימני
            t=5,  # גבול עליון
            b=5  # גבול תחתון
        ),
        plot_bgcolor='#34495e',  # Set plot background color
        font=dict(color='white')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig
