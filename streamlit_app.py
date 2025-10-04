import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Live Election Results", layout="wide")

@st.cache_resource
def get_google_sheet_connection():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=5)
def load_data_from_sheets(_client, sheet_url, worksheet_name="Sheet1"):
    sheet = _client.open_by_url(sheet_url)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def create_bar_chart(df):
    colors = ['#7FDBDA', '#4DB8D8', '#3B9BC4', '#2E5F8C']
    candidate_col = 'Candidates' if 'Candidates' in df.columns else 'Candidate'
    
    fig = go.Figure(data=[
        go.Bar(
            x=df[candidate_col],
            y=df['Votes'],
            marker_color=colors[:len(df)],
            text=df['Votes'],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Candidate Votes",
        xaxis_title="",
        yaxis_title="Votes",
        showlegend=False,
        height=500,
        plot_bgcolor='white',
        font=dict(size=14)
    )
    
    return fig

def main():
    st.title("Live Election Results Dashboard")
    
    st.sidebar.header("Configuration")
    sheet_url = st.sidebar.text_input(
        "Google Sheet URL",
        value="https://docs.google.com/spreadsheets/d/15Lh2DmXAnBr9Aw1YHlNW31Tj3M9yvf7po7k9hl1s434/edit"
    )
    worksheet_name = st.sidebar.text_input("Worksheet Name", value="Sheet1")
    
    try:
        client = get_google_sheet_connection()
        df = load_data_from_sheets(client, sheet_url, worksheet_name)
        
        if df is not None and not df.empty:
            fig = create_bar_chart(df)
            st.plotly_chart(fig, use_container_width=True)
            
            status_container = st.empty()
            status_container.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(480)
            st.rerun()
        else:
            st.error("No data available")
            
    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main() 