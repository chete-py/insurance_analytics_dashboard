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

def chart_time(df):
    # Group by day and time range
    time_range_labels = ['00:00 - 03:00', '03:00 - 06:00', '06:00 - 09:00', '09:00 - 12:00',
                         '12:00 - 15:00', '15:00 - 18:00', '18:00 - 21:00', '21:00 - 00:00']
    time_range_bins = pd.interval_range(start=pd.to_timedelta('00:00:00'), end=pd.to_timedelta('24:00:00'), freq='3H')
    df['Time Range'] = pd.cut(pd.to_timedelta(df['Time of Loss']), bins=time_range_bins, labels=time_range_labels, include_lowest=True)

    # Get the counts for each time range
    time_counts = df.groupby('Time Range')['Claim Type'].value_counts().reset_index(name='count')

    # Create a DataFrame for the missing time
    missing_time_df = pd.DataFrame({
        'Time Range': 'Missing Time',
        'Claim Type': 'Missing Time',
        'count': [df.loc[df['Time of Loss'] == '00:00:01', 'Claim Type'].count()]
    })

    # Concatenate the missing time DataFrame with the counts DataFrame
    time_counts = pd.concat([missing_time_df, time_counts])

    # Create the chart
    chart = px.bar(time_counts, x='Time Range', y='count', color='Claim Type',
                   title='Claim Frequency by Time Range')
    chart.update_layout(legend=dict(orientation='v', font=dict(size=8)))
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
