import pandas as pd
import plotly.graph_objs as go

def create_general_pie_chart(df):
    # יצירת גרף פאי עם הנתונים מהטבלה
    labels = df.columns  # שמות העמודות
    values = df.iloc[0]  # ערכים בשורה הראשונה

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

    # הגדרת תצוגת הגרף
    fig.update_layout(
        plot_bgcolor='#34495e',  # צבע רקע של הגרף
        paper_bgcolor='#34495e',  # צבע רקע של הדף
        font=dict(color='white'),
        autosize=True,  # מאפשר ל-Plotly להגדיר את מידות הגרף אוטומטית
        margin=dict(
            l=0,  # גבול שמאלי
            r=0,  # גבול ימני
            t=0,  # גבול עליון
            b=0   # גבול תחתון
        ),
        height=None,  # הגובה מוגדר אוטומטית
        width=None,   # הרוחב מוגדר אוטומטית
        annotations=[
            dict(
                text="Types of website visitors",  # הטקסט שיופיע בתוך הגרף
                x=0.95,  # מיקום אופקי של הטקסט (צד ימין)
                y=0.05,  # מיקום אנכי של הטקסט (צד תחתון)
                font=dict(size=15, color='white'),  # גודל וצבע הפונט
                showarrow=False  # ללא חץ מצביע
            )
        ]
    )

    return fig

