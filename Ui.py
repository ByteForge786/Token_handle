# Initialize token manager
@st.cache_resource
def get_token_manager():
    token_manager = TokenManager(token_url=TOKEN_URL)
    # Force initialize session state variables on every page load
    if 'token_request_count' not in st.session_state:
        st.session_state.token_request_count = 0
    if 'token_refresh_count' not in st.session_state:
        st.session_state.token_refresh_count = 0
    if 'token_error_count' not in st.session_state:
        st.session_state.token_error_count = 0
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    return token_manager

# Get token manager instance
token_manager = get_token_manager()


import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import hashlib
import logging
import requests
from token_manager import TokenManager

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
CSV_FILE = 'user_interactions.csv'
TOKEN_URL = "YOUR_TOKEN_URL_HERE"  # Replace with your token URL
SQL_API_URL = "YOUR_SQL_API_ENDPOINT"  # Replace with your SQL API endpoint
USERNAME = "YOUR_USERNAME"  # Replace with your username

# Initialize token manager
@st.cache_resource
def get_token_manager():
    return TokenManager(token_url=TOKEN_URL)

# Get token manager instance
token_manager = get_token_manager()

def generate_sql(question):
    """Generate SQL using API with automatic token refresh."""
    try:
        # Get fresh token (automatically handles refresh if needed)
        token = token_manager.get_token()
        
        # Make API call with token
        headers = {
            "Authorization": f"Bearer {token}",
            "Username": USERNAME
        }
        
        response = requests.post(
            SQL_API_URL,
            json={"question": question},
            headers=headers
        )
        response.raise_for_status()
        return response.json()["sql"]
    except Exception as e:
        logging.error(f"Error generating SQL: {str(e)}")
        raise

def execute_query(sql):
    """Execute the generated SQL query."""
    # Your actual query execution logic here
    return pd.DataFrame({'Result': ['Sample Result 1', 'Sample Result 2']})

def handle_interaction(question, result):
    new_data = pd.DataFrame({
        'timestamp': [datetime.now()],
        'question': [question.strip().replace('\n', ' ')],
        'result': [result.strip().replace('\n', ' ')],
        'session_id': [st.session_state['session_id']]
    })
    # Your existing interaction handling code...

def main():
    st.set_page_config(page_title="NhanceBot", layout="wide")
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = hashlib.md5(str(datetime.now()).encode()).hexdigest()
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Title and description
    st.title("💡 SQL Query Generator")
    st.markdown("Ask questions in natural language and get SQL queries!")

    # Main input area
    user_input = st.text_area("Enter your question:", height=100)

    # Generate SQL button
    if st.button("🚀 Generate SQL", use_container_width=True):
        if not user_input:
            st.warning("Please enter a question first!")
            return
            
        try:
            with st.spinner("Generating SQL..."):
                # This will automatically handle token refresh
                sql_response = generate_sql(user_input)
                
            # Display SQL
            st.success("SQL Generated Successfully!")
            st.code(sql_response, language="sql")
            
            # Execute query
            with st.spinner("Executing query..."):
                result_df = execute_query(sql_response)
                st.dataframe(result_df)
                
            # Update chat history
            st.session_state['chat_history'].append({
                'question': user_input,
                'sql': sql_response,
                'result': result_df,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Handle interaction
            handle_interaction(user_input, sql_response)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logging.error(f"Error processing query: {str(e)}")

    # Display chat history
    if st.session_state['chat_history']:
        st.markdown("### Previous Queries")
        for item in reversed(st.session_state['chat_history']):
            with st.expander(f"🔍 {item['question'][:50]}...", expanded=False):
                st.text(f"Time: {item['timestamp']}")
                st.code(item['sql'], language="sql")
                st.dataframe(item['result'])

if __name__ == "__main__":
    main()
