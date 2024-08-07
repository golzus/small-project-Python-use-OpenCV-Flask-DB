import pandas as pd
import plotly.express as px

def create_graph(selected_categories):
    file_path = 'excelsFiles/excelLoadsPerHours.xlsx'
    df = pd.read_excel(file_path,engine='openpyxl')
    df_melted = df.melt(id_vars=[df.columns[0]], value_vars=selected_categories, var_name='category',
                        value_name='count')

    fig = px.scatter(df_melted, x="category", y="count", animation_frame=df.columns[0],
                     range_y=[0, df_melted['count'].max() + 5], size="count", size_max=30)

    fig.update_layout(
        margin=dict(
            l=5,  # גבול שמאלי
            r=5,  # גבול ימני
            t=18,  # גבול עליון
            b=5  # גבול תחתון
        ),
        annotations=[
            dict(
                text="Loads of people/ vehicles per hour",  # הטקסט שיופיע בתוך הגרף
                x=0,  # מיקום אופקי של הטקסט (צד ימין)
                y=20,  # מיקום אנכי של הטקסט (צד תחתון)
                font=dict(size=15, color='white'),  # גודל וצבע הפונט
                showarrow=False  # ללא חץ מצביע
            )
        ]
,
    plot_bgcolor='#34495e',  # Set plot background color
        paper_bgcolor='#34495e',  # Set paper background color
        font=dict(color='white'),  # Set font color to white
        xaxis=dict(showgrid=True, gridcolor='gray'),  # Show x-axis grid lines
        yaxis=dict(showgrid=True, gridcolor='gray')   # Show y-axis grid lines

    )

    fig.update_traces(marker=dict())  # Update marker color

    return fig
