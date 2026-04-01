"""
Management Tab View — Tab 3
Handles Add/Update/Delete for Employees and Projects.
"""

import streamlit as st
import pandas as pd
from db.employees import get_employees, add_employee, update_employee, delete_employee
from db.projects import get_projects, add_project, update_project, delete_project


def render():
    st.header("⚙️ Management")
    st.info("""
    **Instructions:** Use the sections below to add, update, or delete employees and projects.
    Expand each section to access the form.
    """)

    # ── Add Employee ──
    with st.expander("➕ Add New Employee", expanded=False):
        st.subheader("Employee Information")
        
        if st.session_state.employee_success:
            st.success(st.session_state.employee_success)
            st.session_state.employee_success = None
        
        with st.form("employee_addition_form"):
            col1, col2 = st.columns(2)
            with col1:
                emp_name = st.text_input("Employee Name:", placeholder="Enter full name")
            with col2:
                emp_phone = st.text_input("Phone Number:", placeholder="e.g., 555-0101")
            emp_wage = st.number_input("Base Wage (PKR/unit):", min_value=0.0, step=0.25, format="%.2f")

            submitted = st.form_submit_button("💾 Save Entry", width='stretch')
        if submitted:
            if not emp_name:
                st.warning("⚠️ Please enter an employee name.")
            elif not emp_phone:
                st.warning("⚠️ Please enter a phone number.")
            elif emp_wage <= 0:
                st.warning("⚠️ Please enter a valid base wage greater than 0.")
            else:
                if add_employee(emp_name, emp_phone, emp_wage):
                    st.session_state.employee_success = f"✅ Employee '{emp_name}' added successfully!"
                    st.rerun()
                else:
                    st.error("❌ Failed to add employee.")

    # ── Add Project ──
    with st.expander("➕ Add New Project", expanded=False):
        st.subheader("Project Information")
        if st.session_state.project_success:
            st.success(st.session_state.project_success)
            st.session_state.project_success = None
        
        with st.form("project_entry_form"):
            project_name = st.text_input("Project Name:", placeholder="Enter project name")
            submitted = st.form_submit_button("💾 Save Entry", width='stretch')
        if submitted:
            if not project_name:
                st.warning("⚠️ Please enter a project name.")
            else:
                if add_project(project_name):
                    st.session_state.project_success = f"✅ Project '{project_name}' added successfully!"
                    st.rerun()
                else:
                    st.error("❌ Failed to add project.")

    # ── Update Employee ──
    with st.expander("✏️ Update Employee", expanded=False):
        st.subheader("Update Employee Information")
        employees = get_employees()
        if employees:
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] for e in employees}
            selected_emp = st.selectbox("Select Employee to Update:", options=list(employee_options.keys()))
            employee_id = employee_options[selected_emp]
            current_emp = next((e for e in employees if e['employee_id'] == employee_id), None)

            if current_emp:
                
                if st.session_state.update_employee_success:
                    st.success(st.session_state.update_employee_success)
                    st.session_state.update_employee_success = None
                with st.form("update_employee_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        updated_name = st.text_input("Employee Name:", value=current_emp['name'], key="update_emp_name")
                    with col2:
                        updated_phone = st.text_input("Phone Number:", value=current_emp.get('phone', ''), key="update_emp_phone")
                    updated_wage = st.number_input("Base Wage (PKR/unit):", min_value=0.0, step=0.25,
                                                value=float(current_emp['base_wage']), format="%.2f", key="update_emp_wage")
                    submitted = st.form_submit_button("💾 Save Entry", width='stretch')
                if submitted:
                    if not updated_name:
                        st.warning("⚠️ Please enter an employee name.")
                    elif not updated_phone:
                        st.warning("⚠️ Please enter a phone number.")
                    elif updated_wage <= 0:
                        st.warning("⚠️ Please enter a valid base wage greater than 0.")
                    else:
                        if update_employee(employee_id, updated_name, updated_phone, updated_wage):
                            st.session_state.update_employee_success = f"✅ Employee '{updated_name}' updated successfully!"
                            st.rerun()
                        else:
                            st.error("❌ Failed to update employee.")
        else:
            st.info("No employees available to update.")

    # ── Delete Employee ──
    with st.expander("🗑️ Delete Employee", expanded=False):
        st.subheader("Delete Employee")
        employees = get_employees()
        if employees:
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] for e in employees}
            selected_emp = st.selectbox("Select Employee to Delete:", options=list(employee_options.keys()), key="delete_emp_select")
            employee_id = employee_options[selected_emp]
            emp_name = next((e['name'] for e in employees if e['employee_id'] == employee_id), "Unknown")

            if st.session_state.delete_employee_success:
                st.success(st.session_state.delete_employee_success)
                st.session_state.delete_employee_success = None

            confirm_delete = st.checkbox(f"I confirm I want to delete employee: {emp_name}", key="confirm_delete_emp")

            if st.button("🗑️ Delete Employee", type="primary", width='stretch', key="delete_emp_btn"):
                if not confirm_delete:
                    st.warning("⚠️ Please confirm deletion by checking the checkbox.")
                else:
                    if delete_employee(employee_id):
                        st.session_state.delete_employee_success = f"✅ Employee '{emp_name}' deleted successfully!"
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete employee.")
        else:
            st.info("No employees available to delete.")

    # ── Update Project ──
    with st.expander("✏️ Update Project", expanded=False):
        st.subheader("Update Project Information")
        projects = get_projects()
        if projects:
            project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] for p in projects}
            selected_proj = st.selectbox("Select Project to Update:", options=list(project_options.keys()), key="update_proj_select")
            project_id = project_options[selected_proj]
            current_proj = next((p for p in projects if p['project_id'] == project_id), None)

            if current_proj:
                updated_project_name = st.text_input("Project Name:", value=current_proj['project_name'], key="update_proj_name")

                if st.session_state.update_project_success:
                    st.success(st.session_state.update_project_success)
                    st.session_state.update_project_success = None

                if st.button("💾 Update Project", type="primary", width='stretch', key="update_proj_btn"):
                    if not updated_project_name:
                        st.warning("⚠️ Please enter a project name.")
                    else:
                        if update_project(project_id, updated_project_name):
                            st.session_state.update_project_success = f"✅ Project '{updated_project_name}' updated successfully!"
                            st.rerun()
                        else:
                            st.error("❌ Failed to update project.")
        else:
            st.info("No projects available to update.")

    # ── Delete Project ──
    with st.expander("🗑️ Delete Project", expanded=False):
        st.subheader("Delete Project")
        projects = get_projects()
        if projects:
            project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] for p in projects}
            selected_proj = st.selectbox("Select Project to Delete:", options=list(project_options.keys()), key="delete_proj_select")
            project_id = project_options[selected_proj]
            proj_name = next((p['project_name'] for p in projects if p['project_id'] == project_id), "Unknown")
            print(project_name)
            print(project_id)
            if st.session_state.delete_project_success:
                st.success(st.session_state.delete_project_success)
                st.session_state.delete_project_success = None

            confirm_delete = st.checkbox(f"I confirm I want to delete project: {proj_name}", key="confirm_delete_proj")

            if st.button("🗑️ Delete Project", type="primary", width = 'stretch', key="delete_proj_btn"):
                if not confirm_delete:
                    st.warning("⚠️ Please confirm deletion by checking the checkbox.")
                else:
                    if delete_project(project_id):
                        st.session_state.delete_project_success = f"✅ Project '{proj_name}' deleted successfully!"
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete project.")
        else:
            st.info("No projects available to delete.")

    # ── Current Data ──
    st.markdown("---")
    st.subheader("📋 Current Data")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current Employees:**")
        employees = get_employees()
        if employees:
            emp_df = pd.DataFrame(employees)
            st.dataframe(emp_df[['employee_id', 'name', 'phone', 'base_wage']], width = 'stretch', hide_index=True)
        else:
            st.info("No employees added yet.")

    with col2:
        st.write("**Current Projects:**")
        projects = get_projects()
        if projects:
            proj_df = pd.DataFrame(projects)
            st.dataframe(proj_df, width = 'stretch', hide_index=True)
        else:
            st.info("No projects added yet.")