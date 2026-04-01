"""
Reports & Settlement Database Operations
=========================================
This file handles all the complex queries that involve multiple tables.

SUPABASE JOIN PATTERN:
    Instead of writing SQL JOINs, Supabase lets you fetch related tables
    by listing them in .select() using their foreign key relationship.

    Example — fetching wage_entries WITH employee and project data:

        client.table("wage_entries")
            .select("*, employees(name, base_wage), projects(project_name)")
            .execute()

    This returns each wage entry with nested dicts:
        {
            "entry_id": 1001,
            "wage_units": 3.5,
            "advance_taken": 500,
            "date_worked": "2025-03-01",
            "employees": {"name": "John", "base_wage": 800.0},
            "projects":  {"project_name": "Building A"}
        }

    You then FLATTEN this in Python to match your old report format.

FLATTENING EXAMPLE:
    raw = response.data
    report = []
    for row in raw:
        report.append({
            "employee_name":         row["employees"]["name"],
            "project_name":          row["projects"]["project_name"],
            "base_wage":             row["employees"]["base_wage"],
            "wage_units":            row["wage_units"],
            "advance_taken":         row["advance_taken"],
            "calculated_settlement": (row["wage_units"] * row["employees"]["base_wage"]) - row["advance_taken"]
        })
    return report
"""

from db.connection import get_client
import streamlit as st


def get_contractor_id():
    """Helper to get the logged in contractor's ID from session."""
    return st.session_state.contractor["contractor_id"]


def get_settlement_report():
    """
    Detailed settlement report — all entries with employee and project info.

    Returns list of dicts with:
        employee_id, employee_name, project_id, project_name,
        date_worked, wage_units, base_wage, advance_taken, calculated_settlement
    """
    # ✅ DONE FOR YOU — read the flattening carefully, you'll need it below
    if "settlement_report" in st.session_state:
        return st.session_state.settlement_report
    try:
        client = get_client()
        response = client.table("wage_entries") \
            .select("*, employees(employee_id, name, base_wage), projects(project_id, project_name)") \
            .eq("contractor_id", get_contractor_id()) \
            .order("employee_id") \
            .execute()

        report = []
        for row in response.data:
            emp = row.get("employees") or {}
            proj = row.get("projects") or {}
            report.append({
                "employee_id":           emp.get("employee_id"),
                "employee_name":         emp.get("name"),
                "project_id":            proj.get("project_id"),
                "project_name":          proj.get("project_name"),
                "date_worked":           row["date_worked"],
                "wage_units":            row["wage_units"],
                "base_wage":             emp.get("base_wage", 0),
                "advance_taken":         row["advance_taken"],
                "calculated_settlement": (row["wage_units"] * emp.get("base_wage", 0)) - row["advance_taken"]
            })
        st.session_state.settlement_report = report
        return report
    except Exception as e:
        print(f"Error generating settlement report: {e}")
        return []


def get_settlement_summary_by_employee():
    """
    Summary grouped by employee — total units, advance, and settlement per employee.

    Returns list of dicts with:
        employee_id, employee_name, total_wage_units,
        base_wage, total_advance_taken, total_settlement

    📝 YOUR TURN:
    - Fetch from "wage_entries" selecting employees(employee_id, name, base_wage)
    - Add .eq("contractor_id", get_contractor_id()) to filter by logged in contractor
    - Flatten and group by employee_id in Python using a dict
    - For each employee accumulate: total_wage_units, total_advance_taken
    - Calculate total_settlement = (total_wage_units * base_wage) - total_advance_taken
    HINT: Use a dict keyed by employee_id to group, then return dict.values()
    """
    if "settlement_report_by_employee" in st.session_state:
        return st.session_state.settlement_report_by_employee
    try:
        client = get_client()
        response = client.table("wage_entries").select("*, employees(employee_id, name, base_wage)") \
        .eq("contractor_id", get_contractor_id()) \
        .execute()
        # Start with an empty dict — this will hold one entry per employee
        grouped = {}

        for row in response.data:
            emp = row.get("employees") or {}
            emp_id = emp.get("employee_id")

            if emp_id not in grouped:
                # First time seeing this employee — create their entry
                grouped[emp_id] = {
                    "employee_id":       emp_id,
                    "employee_name":     emp.get("name"),
                    "base_wage":         emp.get("base_wage", 0),
                    "total_wage_units":  0,      # start at 0, will accumulate
                    "total_advance_taken": 0     # start at 0, will accumulate
                }

            # Whether first time or not — ADD to their running totals
            grouped[emp_id]["total_wage_units"]    += row["wage_units"]
            grouped[emp_id]["total_advance_taken"] += row["advance_taken"]

        # Now calculate final settlement for each employee
        result = []
        for emp in grouped.values():
            emp["total_settlement"] = (emp["total_wage_units"] * emp["base_wage"]) - emp["total_advance_taken"]
            result.append(emp)
        st.session_state.settlement_report_by_employee = result
        return result
    except Exception as e:
        print(f"Error Generaing report: {e}")

def get_settlement_by_project(project_id: int):
    """
    All wage entries for a specific project.

    Args:
        project_id: ID of the project to filter by

    Returns list of dicts with:
        employee_id, employee_name, project_id, project_name,
        date_worked, wage_units, base_wage, advance_taken, calculated_settlement

    📝 YOUR TURN:
    - Same as get_settlement_report() above BUT add:
      .eq("project_id", project_id) AND .eq("contractor_id", get_contractor_id())
    - Flatten the same way
    HINT: It's basically get_settlement_report() with two extra filter lines!
    """
    if "settlement_report_by_project" in st.session_state:
        return st.session_state.settlement_report_by_project
    try:
        client = get_client()
        response = client.table("wage_entries") \
            .select("*, employees(employee_id, name, base_wage), projects(project_id, project_name)") \
            .eq("contractor_id", get_contractor_id()) \
            .eq("project_id", project_id) \
            .order("employee_id") \
            .execute()

        report = []
        for row in response.data:
            emp = row.get("employees") or {}
            proj = row.get("projects") or {}
            report.append({
                "employee_id":           emp.get("employee_id"),
                "employee_name":         emp.get("name"),
                "project_id":            proj.get("project_id"),
                "project_name":          proj.get("project_name"),
                "date_worked":           row["date_worked"],
                "wage_units":            row["wage_units"],
                "base_wage":             emp.get("base_wage", 0),
                "advance_taken":         row["advance_taken"],
                "calculated_settlement": (row["wage_units"] * emp.get("base_wage", 0)) - row["advance_taken"]
            })
        st.session_state.settlement_report_by_project = report
        return report
    except Exception as e:
        print(f"Error generating settlement report: {e}")
        return []



def get_settlement_by_project_employee(project_id: int):
    """
    Employee-wise summary for a specific project.

    Args:
        project_id: ID of the project

    Returns list of dicts with:
        employee_id, employee_name, project_id, project_name,
        total_wage_units, base_wage, total_advance_taken, total_settlement

    📝 YOUR TURN:
    - Fetch wage_entries filtered by project_id with employees and projects joined
    - Group by employee in Python (like get_settlement_summary_by_employee)
    - But this time also include project_id and project_name in the result
    HINT: Combine the grouping logic from get_settlement_summary_by_employee
          with the project filter from get_settlement_by_project
    """
    cache_key = f"settlement_report_by_project_employee_{project_id}"
    if cache_key in st.session_state:
        return st.session_state.settlement_report_by_project_employee
    try:
        client = get_client()
        response = client.table("wage_entries") \
            .select("*, employees(employee_id, name, base_wage), projects(project_id, project_name)") \
            .eq("contractor_id", get_contractor_id()) \
            .eq("project_id", project_id) \
            .execute()
 
        grouped = {}
        for row in response.data:
            emp = row.get("employees") or {}
            proj = row.get("projects") or {}
            emp_id = emp.get("employee_id")
 
            if emp_id not in grouped:
                grouped[emp_id] = {
                    "employee_id":         emp_id,
                    "employee_name":       emp.get("name"),
                    "project_id":          proj.get("project_id"),
                    "project_name":        proj.get("project_name"),
                    "base_wage":           emp.get("base_wage", 0),
                    "total_wage_units":    0,
                    "total_advance_taken": 0
                }
 
            grouped[emp_id]["total_wage_units"]    += row["wage_units"]
            grouped[emp_id]["total_advance_taken"] += row["advance_taken"]
 
        result = []
        for emp in grouped.values():
            emp["total_settlement"] = (emp["total_wage_units"] * emp["base_wage"]) - emp["total_advance_taken"]
            result.append(emp)
        st.session_state[cache_key] = result
        return result
    except Exception as e:
        print(f"Error generating project employee summary: {e}")
        return [] 


def get_all_projects_summary():
    """
    Overview of all projects — total employees, entries, and settlement per project.

    Returns list of dicts with:
        project_id, project_name, total_employees,
        total_entries, total_wage_units, total_advance_taken, total_settlement

    📝 YOUR TURN:
    - Fetch wage_entries selecting employees(base_wage) and projects(project_id, project_name)
    - Group by project_id in Python
    - For each project track:
        total_employees  → use a set() of employee_ids to count unique employees
        total_entries    → count rows
        total_wage_units → sum wage_units
        total_advance    → sum advance_taken
        total_settlement → sum (wage_units * base_wage) - advance_taken
    HINT: Use a set for unique employee counting: employee_ids.add(row["employee_id"])
          then total_employees = len(employee_ids)
    """
    if "all_projects_summary" in st.session_state:
        return st.session_state.all_projects_summary
    try:
        client = get_client()
        response = client.table("wage_entries") \
            .select("*, employees(base_wage), projects(project_id, project_name)") \
            .eq("contractor_id", get_contractor_id()) \
            .execute()
 
        grouped = {}
        for row in response.data:
            emp = row.get("employees") or {}
            proj = row.get("projects") or {}
            proj_id = proj.get("project_id")
 
            if proj_id not in grouped:
                grouped[proj_id] = {
                    "project_id":          proj_id,
                    "project_name":        proj.get("project_name"),
                    "total_employees":     set(),
                    "total_entries":       0,
                    "total_wage_units":    0,
                    "total_advance_taken": 0,
                    "total_settlement":    0
                }
 
            grouped[proj_id]["total_employees"].add(row["employee_id"])
            grouped[proj_id]["total_entries"]       += 1
            grouped[proj_id]["total_wage_units"]    += row["wage_units"]
            grouped[proj_id]["total_advance_taken"] += row["advance_taken"]
            grouped[proj_id]["total_settlement"]    += (row["wage_units"] * emp.get("base_wage", 0)) - row["advance_taken"]
 
        result = []
        for proj in grouped.values():
            proj["total_employees"] = len(proj["total_employees"])
            result.append(proj)
        st.session_state.all_projects_summary = result
        return result
    except Exception as e:
        print(f"Error generating projects summary: {e}")
        return []
 
def get_expense_summary_by_project():
    """
    Summary of expenses grouped by project — total amount spent per project.
 
    Returns list of dicts with:
        project_id, project_name, total_items, total_amount
    """
    if "expense_summary_by_project" in st.session_state:
        return st.session_state.expense_summary_by_project
    try:
        client = get_client()
        response = client.table("expense_entries") \
            .select("*, projects(project_id, project_name)") \
            .eq("contractor_id", get_contractor_id()) \
            .execute()
 
        grouped = {}
        for row in response.data:
            proj = row.get("projects") or {}
            proj_id = proj.get("project_id")
 
            if proj_id not in grouped:
                grouped[proj_id] = {
                    "project_id":    proj_id,
                    "project_name":  proj.get("project_name"),
                    "total_items":   0,
                    "total_amount":  0.0
                }
 
            grouped[proj_id]["total_items"]  += 1
            grouped[proj_id]["total_amount"] += row.get("amount", 0)
 
        result = list(grouped.values())
        st.session_state.expense_summary_by_project = result
        return result
    except Exception as e:
        print(f"Error generating expense summary: {e}")
        return []







































