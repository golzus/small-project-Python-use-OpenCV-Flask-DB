import pandas as pd
import plotly.express as px

def create_line_chart():
    df = pd.read_excel('static/excelsFiles/excelPerAge.xlsx', engine='openpyxl')
    fig = px.line(df, x='age ranges', y=['women', 'men'], labels={'value':'Count', 'variable':'Gender'})
    fig.update_layout(
    annotations=[
            dict(
                text="Classification of people by age ranges",  # הטקסט שיופיע בתוך הגרף
                x=2,  # מיקום אופקי של הטקסט (צד ימין)
                y=7,  # מיקום אנכי של הטקסט (צד תחתון)
                font=dict(size=15, color='white'),  # גודל וצבע הפונט
                showarrow=False  # ללא חץ מצביע
            )
        ],
        paper_bgcolor='#34495e',
        plot_bgcolor='#34495e',
        font=dict(color='white'),
        margin=dict(l=5, r=5, t=5, b=5)
    )
    return fig
