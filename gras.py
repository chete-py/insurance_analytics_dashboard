import streamlit as st
import plotly_express as px
import numpy as np
import pandas as pd
from datetime import datetime

# configuration
st.set_option('deprecation.showfileUploaderEncoding', False)

# title of the app
st.title("Gras Savoye Client Claims Analytics ")

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
        df.dropna(subset=['Claim No'], inplace=True)
        df['Claim Type'] = df['Claim Type'].str.replace('^Work Injury', 'WIBA', regex=True)

        df['Frequency'] = np.bool_(1)
        
        st.dataframe(df.head(5))

     

       
    except Exception as e:
        st.write("Error:", e)

def chart_day(df):
    top_claims = df.groupby('Day')['Claim Type'].value_counts().groupby('Day').head(3).reset_index(name='count')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    top_claims['Day'] = pd.Categorical(top_claims['Day'], categories=weekdays, ordered=True)
    chart = px.bar(top_claims, x='Day', y='count', color='Claim Type', barmode='group', 
                   title='Top 3 Claim Types by Day of Week')
    chart.update_layout(legend=dict(orientation='v', font=dict(size=8)))
    return chart




def chart_month(df):
    chart = px.histogram(df, x='Month', color='Month', category_orders={'Month': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']})
    return chart

def chart_year(df):
    chart = px.histogram(df, x='Year', color='Year')
    return chart



# Define chart selection dropdown
chart_select = st.sidebar.selectbox(
            label="Select a chart",
            options=["Day of Week Analysis", "Month of Incident Analysis", "Yearly Claim Analysis"]
        )

# Call the corresponding chart function based on user selection
if uploaded_file is not None:
    if chart_select == "Day of Week Analysis":
        st.plotly_chart(chart_day(df))
        max_day = df['Day'].mode()[0]
        count_max_day = df['Day'].value_counts()[max_day]
        st.write(f"The day of the week with the most claims is **{max_day}**, with **{count_max_day}** claims.")
        
    elif chart_select == "Month of Incident Analysis":
        st.plotly_chart(chart_month(df))
        max_month = df['Month'].mode()[0]
        count_max_month = df['Month'].value_counts()[max_month]
        st.write(f"The month with the most claims is **{max_month}**, with **{count_max_month}** claims.")
        
    elif chart_select == "Yearly Claim Analysis":
        st.plotly_chart(chart_year(df))
   
    else:
        st.write("Failed to load data from the uploaded file.")
else:
    st.write("Please upload a file to visualize.")
