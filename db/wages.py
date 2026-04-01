"""
Wage Entries Database Operations
==================================
YOUR TASK: Complete the function below.

REMINDER OF THE PATTERN:
    client.table("wage_entries").insert({dict}).execute()

    For dates, Supabase accepts Python date objects or "YYYY-MM-DD" strings.
    To convert: str(date_worked)  →  "2025-03-29"
"""

from datetime import date
import streamlit as st
from db.connection import get_client


def get_contractor_id():
    """Helper to get the logged in contractor's ID from session."""
    return st.session_state.contractor["contractor_id"]


def add_wage_entry(project_id: int, employee_id: int, date_worked: date,
                   wage_units: float, advance_taken: int = 0) -> bool:
    """
    Add a new wage entry linked to the logged in contractor.
    """
    # ✅ DONE FOR YOU
    try:
        client = get_client()
        client.table("wage_entries").insert({
            "contractor_id": get_contractor_id(),
            "project_id": project_id,
            "employee_id": employee_id,
            "date_worked": str(date_worked),
            "wage_units": wage_units,
            "advance_taken": advance_taken
        }).execute()
        st.session_state.pop("settlement_report", None)
        st.session_state.pop("employee_summary", None)
        st.session_state.pop("project_summary", None)
        st.session_state.pop("project_employee_summary", None)
        st.session_state.pop("all_projects_summary", None)
        return True
    except Exception as e:
        print(f"Error adding wage entry: {e}")
        return False
