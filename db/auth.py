"""
Authentication Database Operations
=====================================
Handles contractor login verification.

HOW TO ADD A NEW CLIENT (you do this manually in Supabase dashboard):
    Table: contractors
    Insert a row:
        contractor_id  → e.g. "CTR-001"
        password       → e.g. "mypassword123"
        business_name  → e.g. "Ali Construction Co."
        is_active      → true
"""

from db.connection import get_client
import streamlit as st

def verify_login(contractor_id: str, password: str):
    """
    Verify contractor credentials.

    Args:
        contractor_id: The unique ID you assigned to the contractor
        password:      Their plain text password

    Returns:
        dict with contractor info if valid and active, None otherwise
        e.g. {"contractor_id": "CTR-001", "business_name": "Ali Construction"}
    """
    try:
        client = get_client()
        response = client.table("contractors") \
            .select("contractor_id, business_name, is_active") \
            .eq("contractor_id", contractor_id) \
            .eq("password", password) \
            .execute()
        print(response.data) 
        if response.data:
            contractor = response.data[0]
            # Check if account is active
            if contractor["is_active"]:
                return contractor
            else:
                return None  # Account disabled by admin
        return None  # Wrong ID or password

    except Exception as e:
        print(f"Error verifying login: {e}")
        return None
