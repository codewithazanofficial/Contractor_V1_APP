"""
Expense Entries Database Operations
=====================================
YOUR TASK: Complete this entire file — it's just one function!

By now you've seen the pattern in:
  - employees.py  (add_employee)
  - wages.py      (add_wage_entry)

This is exactly the same. You've got this! 💪

TABLE NAME: "expense_entries"
COLUMNS:    project_id, item_name, date, units, price_per_unit, notes, amount
"""

from datetime import date
import streamlit as st
from db.connection import get_client


def get_contractor_id():
    """Helper to get the logged in contractor's ID from session."""
    return st.session_state.contractor["contractor_id"]


def add_expense_entry(project_id: int, item_name: str, date_of_transaction: date,
                      units: float, p_p_u: float, notes: str, amount: float) -> bool:
    """
    Add a new expense entry.

    Args:
        project_id:           ID of the project
        item_name:            Name of the item/expense
        date_of_transaction:  Date of the transaction
        units:                Number of units
        p_p_u:                Price per unit
        notes:                Any additional notes
        amount:               Total amount (units * p_p_u)

    Returns:
        True if successful, False otherwise

    
    """
    # 📝 YOUR TURN — you know the pattern now!
    # 1. Get the client
    # 2. Insert into "expense_entries" with ALL fields including:
    #    contractor_id → get_contractor_id()   ← don't forget this!
    #    project_id, item_name, date → str(date_of_transaction),
    #    units, price_per_unit → p_p_u, notes, amount
    # 3. Wrap in try/except, return True/False
    try:
        client = get_client()
        client.table("expense_entries").insert({
            "contractor_id" : get_contractor_id(),
            "project_id" : project_id,
            "item_name" : item_name,
            "date" : str(date_of_transaction),
            "units" : units,
            "price_per_unit" : p_p_u,
            "notes" : notes,
            "amount" : amount
        }).execute()
        st.session_state.pop("settlement_report", None)
        st.session_state.pop("settlement_report_by_employee", None)
        st.session_state.pop("all_projects_summary", None)
        st.session_state.pop("all_projects_summary", None)
        st.session_state.pop("expense_summary_by_project", None) 
        return True
    except Exception as e:
        print(f"Error adding expense entry: {e}")
        return False