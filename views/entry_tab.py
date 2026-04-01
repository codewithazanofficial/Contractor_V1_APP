"""
Entry Tab View — Tab 1
Handles Wage Entry and Expense Entry forms.
"""

import streamlit as st
from datetime import date
from db.projects import get_projects
from db.employees import get_employees
from db.wages import add_wage_entry
from db.expenses import add_expense_entry


def render():
    st.info("""
    **Instructions:** Fill in the form below to record daily wage entries.
    Select a project, employee, enter the date worked, wage units, and any advance taken.
    """)

    projects = get_projects()
    employees = get_employees()

    if not projects or not employees:
        st.warning("⚠️ Please add at least one project and one employee in the Management tab before making entries.")
        return

    # Project selection
    project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] for p in projects}
    selected_project = st.selectbox("Select Project:", options=list(project_options.keys()))
    project_id = project_options[selected_project]

    with st.expander("Wage Entry", expanded=True):
        if st.session_state.get("wage_entry_success"):
            st.success(st.session_state.wage_entry_success)
        st.session_state.wage_entry_success = None
        with st.form("wage_entry_form"):
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] for e in employees}
            selected_employee = st.selectbox("Select Employee:", options=list(employee_options.keys()))
            employee_id = employee_options[selected_employee]

            col3, col4, col5 = st.columns(3)
            with col3:
                date_worked = st.date_input("Date Worked:", value=date.today())
            with col4:
                wage_units = st.number_input("Wage Units:", min_value=0.0, step=0.5, format="%.2f")
            with col5:
                advance_taken = st.number_input("Advance Taken:", min_value=0, step=1, value=0)
            submitted = st.form_submit_button("💾 Save Entry", type='primary', width='stretch', key = 'wage_entry_btn')
        if submitted:
            if add_wage_entry(project_id, employee_id, date_worked, wage_units, advance_taken):
                st.session_state.wage_entry_success = "✅ Wage entry saved successfully!"
                st.rerun()
            else:
                st.error("❌ Failed to save wage entry.")

    with st.expander("Expense Entry"):
        with st.form("expense_entry_form"):
            cola, col7, col8, col9, col10 = st.columns(5)
            with cola:
                item_name = st.text_input("Item Name:", value="None")
            with col7:
                date_of_transaction = st.date_input("Date of Transaction:", value=date.today())
            with col8:
                p_p_u = st.number_input("Price Per Unit:", min_value=0.0, step=0.5, format="%.2f")
            with col9:
                units = st.number_input("Units:", min_value=0.0, step=0.5, format="%.2f")
            with col10:
                notes = st.text_input("Enter Notes if any", value="Nothing to Show")

            amount = p_p_u * units
            submitted = st.form_submit_button("💾 Save Entry",type='primary',  width='stretch', key = 'expense_entry_btn')
        if submitted:
            if add_expense_entry(project_id, item_name, date_of_transaction, units, p_p_u, notes, amount):
                st.success("✅ Transaction successfully added.")
            else:
                st.error("❌ Could not add transaction right now.")
