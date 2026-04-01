"""
Supabase Connection Module
Replaces the old MySQL get_connection() function.
Import this client in every db file instead of creating a new connection.
"""
 
import streamlit as st
from supabase import create_client, Client
 
 
def get_client() -> Client:
    """
    Create and return a Supabase client.
    Reads credentials from Streamlit secrets.
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
 