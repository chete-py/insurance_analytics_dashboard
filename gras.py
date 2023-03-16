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
        
        # Define a function to group the time ranges
        def group_time(time):
            if time == "00:00:01":
                return "Missing Time"
            else:
                hour = datetime.strptime(time, "%H:%M:%S").hour
                if hour >= 0 and hour < 3:
                    return "00:00 - 03:00"
                elif hour >= 3 and hour < 6:
                    return "03:00 - 06:00"
                elif hour >= 6 and hour < 9:
                    return "06:00 - 09:00"
                elif hour >= 9 and hour < 12:
                    return "09:00 - 12:00"
                elif hour >= 12 and hour < 15:
                    return "12:00 - 15:00"
                elif hour >= 15 and hour < 18:
                    return "15:00 - 18:00"
                elif hour >= 18 and hour < 21:
                    return "18:00 - 21:00"
                else:
                    return "21:00 - 00:00"

        # Apply the function to create a new column
        df['Time Range'] = df['Time of Incident'].apply(group_time)
        # Group the data by time range and count the frequency
        time_counts = df.groupby('Time Range').size().reset_index(name='Frequency')

        df['Frequency'] = np.bool_(1)
        
       
        
          
    except Exception as e:
        st.write("Error:", e)

def chart_time(df):
    chart = px.bar(time_counts, x='Time Range', y='Frequency', title='TIME OF INCIDENT ANALYSIS')
    return chart
    
                
def chart_day(df):
    top_claims = df.groupby('Day')['Claim Type'].value_counts().groupby('Day').head(3).reset_index(name='count')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    top_claims['Day'] = pd.Categorical(top_claims['Day'], categories=weekdays, ordered=True)
    top_claims = top_claims.sort_values('Day')
    chart = px.bar(top_claims, x='Day', y='Number of Claims', color='Claim Type', barmode='group', 
                   title='Claim Frequency in top 3 Insurance Classes by Day of Week')
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
            options=["Top 5 Claim Payouts", "Time of Incident Analysis", "Day of Incident Analysis", "Month of Incident Analysis", "Yearly Claim Analysis"]
        )

# Call the corresponding chart function based on user selection
if uploaded_file is not None:
    if chart_select == "Day of Incident Analysis":
        st.plotly_chart(chart_day(df))
        
        
    elif chart_select == "Month of Incident Analysis":
        st.plotly_chart(chart_month(df))
        max_month = df['Month'].mode()[0]
        count_max_month = df['Month'].value_counts()[max_month]
        st.write(f"The month with the most claims is **{max_month}**, with **{count_max_month}** claims.")
        
    elif chart_select == "Yearly Claim Analysis":
        st.plotly_chart(chart_year(df))
        
     elif chart_select == "Time of Incident Analysis":
        st.plotly_chart(chart_time(df))
        
    elif chart_select == "Top 5 Claim Payouts":
        # Get top 3 claim payouts
        top_payouts = df.nlargest(5, 'Amount Paid')

        # Select desired columns
        top_payouts = top_payouts.loc[:, ['Claim No', 'Insurer', 'Year', 'Claim reserve amount', 'Amount Paid']]

        # Display table
        st.table(top_payouts)
   
    else:
        st.write("Failed to load data from the uploaded file.")
else:
    st.write("Please upload a file to visualize.")
