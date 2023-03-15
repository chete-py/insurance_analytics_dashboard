import streamlit as st
import plotly_express as px
import numpy as np
import pandas as pd
from datetime import datetime

# configuration
st.set_option('deprecation.showfileUploaderEncoding', False)

# title of the app
st.title("Data Visualization App")

# Add a sidebar
st.sidebar.image('graslogo.jpg', use_column_width=True)
st.sidebar.subheader("Visualization Settings")

# Setup file upload
uploaded_file = st.sidebar.file_uploader(
    label="Upload your CSV or Excel file. (200MB max)",
    type=['csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file, header=8)
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file, header=8)
              

        # convert date column to month name
        df = df.iloc[1:]
        df['Month'] = pd.to_datetime(df['Loss Date']).dt.month_name()
        df['Day'] = pd.to_datetime(df['Loss Date']).dt.day_name()
        df['Year'] = pd.to_datetime(df['Loss Date']).dt.year
        df['Frequency'] = np.bool_(1)

      

        # check if df is defined
        if 'df' in locals() or 'df' in globals():
            st.write(df)

    except Exception as e:
        st.write("Error:", e)

def chart_day(df):
    
    chart = px.histogram(df, x='Day', color='Day')
    return chart

def chart_month(df):
    chart = px.histogram(df, x='Month', color='Month')
    return chart

def chart_year(df):
    chart = px.histogram(df, x='Year', color='Year')
    return chart

def chart_occupation(df):
    chart = px.pie(df, values='Frequency', names='Claim Position')
    return chart

# Define chart selection dropdown
chart_select = st.sidebar.selectbox(
            label="Select a chart",
            options=["Day of Week Histogram", "Month of Incident", "Year Histogram", "Occupation Pie Chart"]
        )

# Call the corresponding chart function based on user selection
if uploaded_file is not None:
    if chart_select == "Day of Week Histogram":
        st.plotly_chart(chart_day(df))
    elif chart_select == "Month of Incident":
        st.plotly_chart(chart_month(df))
    elif chart_select == "Year Histogram":
        st.plotly_chart(chart_year(df))
    elif chart_select == "Occupation Pie Chart":
        st.plotly_chart(chart_occupation(df))
    else:
        st.write("Failed to load data from the uploaded file.")
else:
    st.write("Please upload a file to visualize.")
