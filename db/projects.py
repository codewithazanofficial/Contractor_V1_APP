"""
Projects Database Operations
==============================
YOUR TASK: Complete the functions below using the same pattern from employees.py.

REMINDER OF THE PATTERN:
    client.table("projects").select("*").execute()          # fetch
    client.table("projects").insert({dict}).execute()       # insert
    client.table("projects").update({dict}).eq(...).execute()  # update
    client.table("projects").delete().eq(...).execute()     # delete

    Always wrap in try/except and return [] or False on error.
"""
# mydatabase_255712
from db.connection import get_client
import streamlit as st


def get_contractor_id():
    """Helper to get the logged in contractor's ID from session."""
    return st.session_state.contractor["contractor_id"]


def get_projects():
    """
    Retrieve all projects for the logged in contractor.

    Returns:
        List of dicts with keys: project_id, project_name
    """
    # ✅ DONE FOR YOU — use this as reference for the functions below
    if "projects" in st.session_state:
        return st.session_state.projects
    try:
        client = get_client()
        response = client.table("projects") \
            .select("project_id, project_name") \
            .eq("contractor_id", get_contractor_id()) \
            .order("project_id") \
            .execute()
        st.session_state.projects = response.data
        return st.session_state.projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []


def add_project(project_name: str):
    """
    Add a new project linked to the logged in contractor.

    Returns:
        True if successful, False otherwise
    """
    # 📝 YOUR TURN:
    # Same as add_employee in employees.py BUT:
    # 1. Table is "projects"
    # 2. Fields are: contractor_id (get_contractor_id()), project_name
    try:
        client = get_client()
        response = client.table("projects").insert({
            "contractor_id" : get_contractor_id(),
            "project_name" : project_name
        }).execute()
        if "employees" in st.session_state:
            st.session_state.projects.append(response.data[0])
        return True
    except Exception as e:
        print(f"Error adding project: {e}")


def update_project(project_id: int, project_name: str) -> bool:
    """
    Update an existing project's name — scoped to logged in contractor.

    Returns:
        True if successful, False otherwise
    """
    # 📝 YOUR TURN:
    # Same as update_employee BUT:
    # 1. Table is "projects"
    # 2. Update field: {"project_name": project_name}
    # 3. Filter by BOTH project_id AND contractor_id (for safety!)
    try:
        client = get_client()
        client.table("projects").update({
            "project_name": project_name
            }).eq("contractor_id", get_contractor_id()).eq("project_id", project_id).execute()
        if "projects" in st.session_state:
            for pro in st.session_state.projects:
                if pro["project_id"] == project_id:
                    pro['project_name'] = project_name
                    break
        return True
    except Exception as e:
        print(f"Error Updating Project: {e}")
        return False
def delete_project(project_id: int) -> bool:
    """
    Delete a project — scoped to logged in contractor for safety.

    Returns:
        True if successful, False otherwise
    """
    # 📝 YOUR TURN:
    # Same as delete_employee BUT:
    # 1. Table is "projects"
    # 2. Filter by BOTH project_id AND contractor_id (for safety!)
    try:
        client = get_client()
        client.table("projects").delete().eq("contractor_id" ,get_contractor_id()) \
        .eq("project_id", project_id).execute()

        if "projects" in st.session_state:
            st.session_state.projects = [
                e for e in st.session_state.projects
                if e["project_id"] != project_id
            ]
        return True
    except Exception as e:
        print(f"Error Deleting Project: {e}")
        return False
