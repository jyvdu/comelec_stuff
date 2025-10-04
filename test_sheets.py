import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os

st.title("🔧 Google Sheets Connection Test")

# Check for credentials file
st.header("1. Checking for credentials...")
if os.path.exists('credentials.json'):
    st.success("✅ Found credentials.json")
    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)
        st.info(f"Service Account: {creds_data.get('client_email')}")
else:
    st.error("❌ credentials.json not found")
    st.stop()

# Try to authenticate
st.header("2. Attempting authentication...")
try:
    # Using google.oauth2 instead of oauth2client (more modern)
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    credentials = Credentials.from_service_account_file(
        'credentials.json',
        scopes=scopes
    )
    
    client = gspread.authorize(credentials)
    st.success("✅ Authentication successful!")
    
except Exception as e:
    st.error(f"❌ Authentication failed: {e}")
    st.stop()

# Try to open the sheet
st.header("3. Attempting to open Google Sheet...")
sheet_url = st.text_input(
    "Google Sheet URL",
    value="https://docs.google.com/spreadsheets/d/15Lh2DmXAnBr9Aw1YHlNW31Tj3M9yvf7po7k9hl1s434/edit"
)

if st.button("Test Connection"):
    try:
        st.info("Opening sheet...")
        sheet = client.open_by_url(sheet_url)
        st.success(f"✅ Sheet opened: {sheet.title}")
        
        st.info("Getting first worksheet...")
        worksheet = sheet.get_worksheet(0)
        st.success(f"✅ Worksheet: {worksheet.title}")
        
        st.info("Reading data...")
        data = worksheet.get_all_records()
        st.success(f"✅ Found {len(data)} rows")
        
        st.dataframe(data)
        
    except gspread.exceptions.APIError as e:
        st.error(f"❌ API Error: {e}")
        if "PERMISSION_DENIED" in str(e):
            st.error("🔒 Permission denied!")
            st.warning("Possible issues:")
            st.write("- Service account doesn't have access to the sheet")
            st.write("- Google Sheets API is not enabled")
            st.write("- Service account is disabled")
    except Exception as e:
        st.error(f"❌ Error: {type(e).__name__}: {e}")

st.header("4. Manual API Check")
st.write("Check if APIs are enabled:")
st.markdown(f"""
- [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=comelec-474015)
- [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com?project=comelec-474015)
""")