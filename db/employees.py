"""
Employees Database Operations
==============================
This file is your REFERENCE — read it carefully before working on
projects.py, wages.py, and expenses.py. The pattern is the same everywhere.

SUPABASE PATTERN:
    client.table("table_name").operation().execute()

    SELECT all:     .select("*").execute()
    SELECT cols:    .select("col1, col2").execute()
    INSERT:         .insert({dict}).execute()
    UPDATE:         .update({dict}).eq("col", value).execute()
    DELETE:         .delete().eq("col", value).execute()

    Results are in: response.data  (always a list of dicts)
"""

import streamlit as st
from db.connection import get_client


def get_contractor_id():
    """Helper to get the logged in contractor's ID from session."""
    return st.session_state.contractor["contractor_id"]


def get_employees():
    """
    Retrieve all employees for the logged in contractor.

    Returns:
        List of dicts with keys: employee_id, name, phone, base_wage
    """
    try:
        client = get_client()
        response = client.table("employees") \
            .select("employee_id, name, phone, base_wage") \
            .eq("contractor_id", get_contractor_id()) \
            .order("employee_id") \
            .execute()
        return response.data
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return []


def add_employee(name: str, phone: str, base_wage: float) -> bool:
    """
    Add a new employee linked to the logged in contractor.

    Args:
        name:       Employee full name
        phone:      Phone number string
        base_wage:  Wage per unit (float)

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_client()
        response = client.table("employees").insert({
            "contractor_id": get_contractor_id(),
            "name": name,
            "phone": phone,
            "base_wage": base_wage
        }).execute()

        # Append the new employee directly to session state
        if "employees" in st.session_state:
            st.session_state.employees.append(response.data[0])
        return True
    except Exception as e:
        print(f"Error adding employee: {e}")
        return False
    # try:
    #     client = get_client()
    #     client.table("employees").insert({
    #         "contractor_id": get_contractor_id(),
    #         "name": name,
    #         "phone": phone,
    #         "base_wage": base_wage
    #     }).execute()
    #     return True
    # except Exception as e:
    #     print(f"Error adding employee: {e}")
    #     return False


def update_employee(employee_id: int, name: str, phone: str, base_wage: float) -> bool:
    """
    Update an existing employee — scoped to logged in contractor for safety.
    """
    try:
        client = get_client()
        client.table("employees").update({
            "name": name,
            "phone": phone,
            "base_wage": base_wage
        }).eq("employee_id", employee_id) \
          .eq("contractor_id", get_contractor_id()) \
          .execute()

        # Update directly in session state
        if "employees" in st.session_state:
            for emp in st.session_state.employees:
                if emp["employee_id"] == employee_id:
                    emp["name"] = name
                    emp["phone"] = phone
                    emp["base_wage"] = base_wage
                    break
        return True
    except Exception as e:
        print(f"Error updating employee: {e}")
        return False
    # try:
    #     client = get_client()
    #     client.table("employees").update({
    #         "name": name,
    #         "phone": phone,
    #         "base_wage": base_wage
    #     }).eq("employee_id", employee_id) \
    #       .eq("contractor_id", get_contractor_id()) \
    #       .execute()
    #     return True
    # except Exception as e:
    #     print(f"Error updating employee: {e}")
    #     return False


def delete_employee(employee_id: int) -> bool:
    """
    Delete an employee — scoped to logged in contractor for safety.
    """
    try:
        client = get_client()
        client.table("employees") \
            .delete() \
            .eq("employee_id", employee_id) \
            .eq("contractor_id", get_contractor_id()) \
            .execute()

        # Remove directly from session state
        if "employees" in st.session_state:
            st.session_state.employees = [
                e for e in st.session_state.employees
                if e["employee_id"] != employee_id
            ]
        return True
    except Exception as e:
        print(f"Error deleting employee: {e}")
        return False
    # try:
    #     client = get_client()
    #     client.table("employees") \
    #         .delete() \
    #         .eq("employee_id", employee_id) \
    #         .eq("contractor_id", get_contractor_id()) \
    #         .execute()
    #     return True
    # except Exception as e:
    #     print(f"Error deleting employee: {e}")
    #     return False
