import streamlit as st
import plotly_express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime

# configuration
st.set_option('deprecation.showfileUploaderEncoding', False)

# title of the app
st.title("Insurance Claims Analytics ")

# Add a sidebar
st.sidebar.image('claimslogo.png', use_column_width=True)
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
        df['Month'] = pd.to_datetime(df['Loss Date']).dt.strftime('%B')
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
                   title='Top 3 Insurance Class Claims On Specific Day Of Week')
    chart.update_layout(legend=dict(orientation='v', font=dict(size=8)))
    chart.update_yaxes(title='Number of Claims')
    return chart

def chart_amountpaid(df, include_empty_ranges=True):
    bins = [-0.1, 0, 50000, 100000, 500000, 1000000, 5000000, np.inf]
    labels = ['NIL', '1 - 50K', '50K - 100K', '100K - 500K', '500K - 1M', '1M - 5M', 'Over 5M']
    df['Amount Range'] = pd.cut(df['Claim reserve amount'], bins=bins, labels=labels)
    
    if include_empty_ranges:
        chart = px.histogram(df, x='Amount Range', color='Amount Range', 
                              category_orders={'Amount Range': labels}, 
                              title='Distribution of Claims Recorded by Amount Paid')
    else:
        df_counts = df['Amount Range'].value_counts().reindex(labels, fill_value=0)
        chart = px.bar(x=df_counts.index, y=df_counts.values, 
                        title='Distribution of Claims Recorded by Amount Paid')
    
    chart.update_yaxes(title='Number of Claims')
    chart.update_xaxes(title='Amount Range')    
    return chart


def chart_month(df):
    chart = px.histogram(df, x='Month', color='Month', category_orders={'Month': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']})
    chart.update_yaxes(title='Number of Claims')
    return chart

def chart_year(df):
    # Group by year and calculate the sum of Claim reserve amount and count of claims
    agg_df = df.groupby('Year').agg({'Claim reserve amount': 'sum', 'Claim No': 'count'}).reset_index()
    agg_df = agg_df.rename(columns={'Claim No': 'Number of Claims'})

    # Find the year with the highest number of claims
    max_count_year = agg_df.loc[agg_df['Number of Claims'].idxmax(), 'Year']

    # Find the year with the highest claim reserve amount
    max_amount_year = agg_df.loc[agg_df['Claim reserve amount'].idxmax(), 'Year']

    # Find the year with the highest claim payment
    max_payment_year = df.loc[df['Claim reserve amount'].idxmax(), 'Year']

    # Create the chart with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=agg_df['Year'], y=agg_df['Number of Claims'], name='Claims Count'), secondary_y=False)
    fig.add_trace(go.Scatter(x=agg_df['Year'], y=agg_df['Claim reserve amount'], name='Amount'), secondary_y=True)

    # Update the layout
    fig.update_layout(title='Comparison Of Annual Number of Claims And Annual Claim Amount',
                      xaxis_title='Year',
                      hovermode='x')
    fig.update_yaxes(title_text='Claims Count', secondary_y=False)
    fig.update_yaxes(title_text='Amount', secondary_y=True)

    # Create the markdown text
    text = f"The year with the highest number of claims is {int(max_count_year)} "
    text += f" while the year with the highest payout is {int(max_amount_year)}. "
    text += f"It is also worth noting the effect of the highest single claim paid that occured in {int(max_payment_year)}."

    # Display the chart and the markdown text
    st.plotly_chart(fig)
    st.markdown(text)
     


# Define chart selection dropdown
chart_select = st.sidebar.selectbox(
            label="Select a chart",
            options=["Brief Description of Data Frame", "Top 5 Claim Payouts", "Amount Paid Analysis", "Day of Week Analysis", "Month of Incident Analysis", "Yearly Claim Analysis"]
        )

# Call the corresponding chart function based on user selection
if uploaded_file is not None:
    if chart_select == "Day of Week Analysis":
        st.plotly_chart(chart_day(df))
        
        
    elif chart_select == "Month of Incident Analysis":
        st.plotly_chart(chart_month(df))
        max_count = df['Month'].value_counts().max()
        max_months = df['Month'].value_counts()[df['Month'].value_counts() == max_count].index.tolist()

        if len(max_months) == 1:
            st.write(f"The month with the most claims is **{max_months[0]}**, with **{max_count}** claims.")
        else:
            st.write(f"There are multiple months with the most claims: {', '.join(max_months)}, each with **{max_count}** claims.")

        
    elif chart_select == "Yearly Claim Analysis":
        st.plotly_chart(chart_year(df))       
        
        
    elif chart_select == "Brief Description of Data Frame":
        # st.write(df)
        num_claims = len(df["Claim No"])
        st.markdown(f"**Total number of claims:** {num_claims}")
        claims_per_type = df.groupby("Claim Type").size()
        st.write(claims_per_type)

        
    elif chart_select == "Amount Paid Analysis":
        st.plotly_chart(chart_amountpaid(df, include_empty_ranges=False))
        no_pay_claims = len(df[df['Claim reserve amount'] == 0])

        # Add sentence to describe claims with no amount paid
        st.markdown(f"It is worth noting that {no_pay_claims} claims had nil Amount Paid. This is probably due to the claim being Report Only, Below Excess, Settlement Pending or absence of data on the payment. ")
        
    elif chart_select == "Top 5 Claim Payouts":
        # Get top 3 claim payouts
        top_payouts = df.nlargest(5, 'Claim reserve amount')

        # Select desired columns
        top_payouts = top_payouts.loc[:, ['Claim Type', 'Loss Date', 'Claim reserve amount', 'Amount Paid']]

       
        # Display styled table
        st.write(top_payouts)
   
    else:
        st.write("Failed to load data from the uploaded file.")
else:
    st.write("Please upload a file to visualize.")
