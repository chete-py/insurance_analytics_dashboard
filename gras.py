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
        mask = df['Claim Type'].str.startswith('Work Injury')
        df.loc[mask, 'Claim Type'] = 'WIBA'

        df['Frequency'] = np.bool_(1)
               
          
    except Exception as e:
        st.write("Error:", e)

def chart_day(df):
    top_claims = df.groupby('Day')['Claim Type'].value_counts().groupby('Day').head(3).reset_index(name='count')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    top_claims['Day'] = pd.Categorical(top_claims['Day'], categories=weekdays, ordered=True)
    top_claims = top_claims.sort_values('Day')
    chart = px.bar(top_claims, x='Day', y='count', color='Claim Type', barmode='group', 
                   title='Top 3 Claim Types by Day of Week')
    chart.update_layout(legend=dict(orientation='v', font=dict(size=8)))
    chart.update_yaxes(title='Number of Claims')
    return chart

def chart_amountpaid(df):
    bins = [0, 50000, 100000, 500000, 1000000, 5000000, np.inf]
    labels = ['1 - 50K', '50K - 100K', '100K - 500K', '500K - 1M', '1M - 5M', 'Over 5M']
    df['Amount Range'] = pd.cut(df['Amount Paid'], bins=bins, labels=labels)
    chart = px.histogram(df, x='Amount Range', color='Amount Range', category_orders={'Amount Range': labels}, title = 'CLAIM PAYOUT RANGE')
    chart.update_yaxes(title='Number of Claims')
    return chart


def chart_month(df):
    chart = px.histogram(df, x='Month', color='Month', category_orders={'Month': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']})
    chart.update_yaxes(title='Number of Claims')
    return chart

def chart_year(df):
    chart = px.histogram(df, x='Year', color='Year')
    chart.update_layout(xaxis={'tickmode': 'linear', 'dtick': 1})
    chart.update_yaxes(title='Number of Claims') 
    return chart


# Define chart selection dropdown
chart_select = st.sidebar.selectbox(
            label="Select a chart",
            options=["Top 5 Claim Payouts", "Amount Paid Analysis", "Day of Week Analysis", "Month of Incident Analysis", "Yearly Claim Analysis"]
        )

# Call the corresponding chart function based on user selection
if uploaded_file is not None:
    if chart_select == "Day of Week Analysis":
        st.plotly_chart(chart_day(df))
        
        
    elif chart_select == "Month of Incident Analysis":
        st.plotly_chart(chart_month(df))
        max_month = df['Month'].mode()[0]
        count_max_month = df['Month'].value_counts()[max_month]
        st.write(f"The month with the most claims is **{max_month}**, with **{count_max_month}** claims.")
        
    elif chart_select == "Yearly Claim Analysis":
        st.plotly_chart(chart_year(df))
        
    elif chart_select == "Amount Paid Analysis":
        st.plotly_chart(chart_amountpaid(df))
        
    elif chart_select == "Top 5 Claim Payouts":
        # Get top 3 claim payouts
        top_payouts = df.nlargest(5, 'Amount Paid')

        # Select desired columns
        top_payouts = top_payouts.loc[:, ['Claim No', 'Insurer', 'Loss Date', 'Claim reserve amount', 'Amount Paid']]

        # Display table
        st.table(top_payouts)
   
    else:
        st.write("Failed to load data from the uploaded file.")
else:
    st.write("Please upload a file to visualize.")
