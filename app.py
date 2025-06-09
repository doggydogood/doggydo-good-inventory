
import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Doggy Do Good Inventory Dashboard", layout="wide")
st.title("📊 Doggy Do Good Inventory Dashboard")

# Sidebar: File upload
st.sidebar.header("Upload Data")
sales_file = st.sidebar.file_uploader("Upload Sales Data (Excel)", type=["xlsx"])

if sales_file:
    xls = pd.ExcelFile(sales_file)
    dashboard_df = pd.read_excel(xls, sheet_name='Dashboard')
    sales_df = pd.read_excel(xls, sheet_name='Sales Summary')
    inventory_df = pd.read_excel(xls, sheet_name='Inventory Levels')
    reorder_df = pd.read_excel(xls, sheet_name='Reorder Plan')

    # Dashboard metrics
    st.subheader("Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Top ASIN (Units)", dashboard_df.iloc[0]['ASIN'])
    col2.metric("Top ASIN Revenue", f"${dashboard_df.iloc[0]['Total Revenue']:,.2f}")

    # Sales Table
    st.subheader("Sales Summary")
    st.dataframe(sales_df.sort_values(by='Total Units Sold', ascending=False))

    # Inventory Table with Low Stock Highlight
    st.subheader("Inventory Levels")
    def highlight_low_stock(val):
        return 'background-color: #ffcccc' if val < 100 else ''
    st.dataframe(inventory_df.style.applymap(highlight_low_stock, subset=['MSL Units']))

    # Reorder Plan
    st.subheader("Reorder Recommendations")
    st.dataframe(reorder_df)

    # Export Reorder CSV
    csv_export = reorder_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Reorder Plan as CSV", data=csv_export, file_name="Reorder_Plan.csv")

    # Slack Integration (manual push)
    st.subheader(":bell: Slack Alert")
    webhook_url = st.text_input("Enter Slack Webhook URL")
    if st.button("Send Weekly Summary to Slack"):
        top_asin = dashboard_df.iloc[0]['ASIN']
        total_revenue = dashboard_df['Total Revenue'].sum()
        message = {
            "text": f"*Doggy Do Good Weekly Summary:*
Top ASIN: `{top_asin}`
Total Revenue: ${total_revenue:,.2f}"
        }
        if webhook_url:
            response = requests.post(webhook_url, json=message)
            if response.status_code == 200:
                st.success("Slack message sent successfully!")
            else:
                st.error("Failed to send message to Slack.")
        else:
            st.warning("Please enter your Slack webhook URL.")
else:
    st.info("Please upload your Excel file to begin.")
