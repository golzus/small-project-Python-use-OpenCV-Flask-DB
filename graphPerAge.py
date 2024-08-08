import pandas as pd
import plotly.express as px
import os


def create_line_chart():
    file_path = 'static/excelsFiles/excelPerAge.xlsx'

    # בדיקת קיום הקובץ
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # טעינת הנתונים מהקובץ
    df = pd.read_excel(file_path, engine='openpyxl')

    # הדפסת השורות הראשונות של ה-DataFrame כדי לראות מה נטען
    print(df.head())

    # בדיקת קיום העמודות הנדרשות
    required_columns = ['age ranges', 'man', 'woman','child']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' is missing from the data.")

    # בדיקת אורכי העמודות
    if len(df['age ranges']) != len(df['man']) or len(df['age ranges']) != len(df['woman']):
        raise ValueError("The lengths of the columns do not match.")

    # יצירת גרף קו עם Plotly Express
    fig = px.line(df, x='age ranges', y=['man', 'woman','child'], labels={'value': 'Count', 'variable': 'Gender'})
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
