"""
Streamlit Application - Company Wage Management System
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date
from database_logic import (
    get_projects,
    get_employees,
    add_wage_entry,
    get_settlement_report,
    get_settlement_summary_by_employee,
    get_settlement_by_project,
    get_settlement_by_project_employee,
    get_all_projects_summary,
    update_employee,
    delete_employee,
    update_project,
    delete_project
)


# Page configuration - wide layout
st.set_page_config(
    page_title="Company Wage Management System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for success messages
if 'employee_success' not in st.session_state:
    st.session_state.employee_success = None
if 'project_success' not in st.session_state:
    st.session_state.project_success = None
if 'wage_entry_success' not in st.session_state:
    st.session_state.wage_entry_success = None
if 'update_employee_success' not in st.session_state:
    st.session_state.update_employee_success = None
if 'update_project_success' not in st.session_state:
    st.session_state.update_project_success = None
if 'delete_employee_success' not in st.session_state:
    st.session_state.delete_employee_success = None
if 'delete_project_success' not in st.session_state:
    st.session_state.delete_project_success = None


def get_connection(database='companydata', host='localhost', user='root', password='new_password'):
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=False  # Explicitly disable autocommit to ensure manual commits work
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None


def add_new_employee(name: str, phone: str, base_wage: float) -> bool:
    """Add a new employee to the database."""
    connection = get_connection()
    success = False
    error_msg = None
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO employees (name, phone, base_wage) VALUES (%s, %s, %s)"
            values = (name, phone, base_wage)
            cursor.execute(query, values)
            # Ensure commit happens before closing cursor
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            error_msg = str(e)
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    else:
        error_msg = "Failed to connect to database"
    
    if error_msg:
        st.error(f"Error adding employee: {error_msg}")
    
    return success


def add_new_project(project_name: str) -> bool:
    """Add a new project to the database."""
    connection = get_connection()
    success = False
    error_msg = None
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO projects (project_name) VALUES (%s)"
            values = (project_name,)
            cursor.execute(query, values)
            # Ensure commit happens before closing cursor
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            error_msg = str(e)
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    else:
        error_msg = "Failed to connect to database"
    
    if error_msg:
        st.error(f"Error adding project: {error_msg}")
    
    return success


# Main title
st.title("💼 Company Wage Management System")
st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(['🏠 Daily Entry', '📊 Reports', '⚙️ Management'])

# ==================== DAILY ENTRY TAB ====================
with tab1:
    st.header("📝 Daily Wage Entry")
    
    st.info("""
    **Instructions:** Fill in the form below to record daily wage entries.
    Select a project, employee, enter the date worked, wage units, and any advance taken.
    """)
    
    # Get current data
    projects = get_projects()
    employees = get_employees()
    
    if not projects or not employees:
        st.warning("⚠️ Please add at least one project and one employee in the Management tab before making entries.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Project selection
            project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] 
                              for p in projects}
            selected_project = st.selectbox(
                "Select Project:",
                options=list(project_options.keys())
            )
            project_id = project_options[selected_project]
        
        with col2:
            # Employee selection
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] 
                               for e in employees}
            selected_employee = st.selectbox(
                "Select Employee:",
                options=list(employee_options.keys())
            )
            employee_id = employee_options[selected_employee]
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            date_worked = st.date_input("Date Worked:", value=date.today())
        
        with col4:
            wage_units = st.number_input("Wage Units:", min_value=0.0, step=0.5, format="%.2f")
        
        with col5:
            advance_taken = st.number_input("Advance Taken:", min_value=0, step=1, value=0)
        
        # Show success message if exists
        if st.session_state.wage_entry_success:
            st.success(st.session_state.wage_entry_success)
            st.session_state.wage_entry_success = None  # Clear after showing
        
        if st.button("💾 Save Entry", type="primary", use_container_width=True):
            if add_wage_entry(project_id, employee_id, date_worked, wage_units, advance_taken):
                st.session_state.wage_entry_success = "✅ Wage entry saved successfully!"
                st.rerun()
            else:
                st.error("❌ Failed to save wage entry. Please check the error message above.")

# ==================== REPORTS TAB ====================
with tab2:
    st.header("📊 Settlement Reports")
    
    st.info("""
    **Instructions:** View detailed settlement reports and summaries.
    The reports show calculated settlements: (wage_units × base_wage) - advance_taken
    """)
    
    report_type = st.radio(
        "Select Report Type:",
        ["Detailed Report", "Summary by Employee", "Project-wise Summary"],
        horizontal=True
    )
    
    if report_type == "Detailed Report":
        st.subheader("📋 Detailed Settlement Report")
        report_data = get_settlement_report()
        
        if report_data:
            # Display as dataframe
            import pandas as pd
            df = pd.DataFrame(report_data)
            
            # Calculate totals before formatting
            total_settlement = df['calculated_settlement'].sum()
            total_advance = df['advance_taken'].sum()
            
            # Format the dataframe for better display
            display_df = df.copy()
            display_df['date_worked'] = pd.to_datetime(display_df['date_worked']).dt.strftime('%Y-%m-%d')
            display_df['base_wage'] = display_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
            display_df['calculated_settlement'] = display_df['calculated_settlement'].apply(lambda x: f"PKR {x:.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entries", len(df))
            with col2:
                st.metric("Total Settlement", f"PKR {total_settlement:.2f}")
            with col3:
                st.metric("Total Advance Taken", f"PKR {total_advance:.2f}")
        else:
            st.info("No wage entries found. Start adding entries in the Daily Entry tab.")
    
    elif report_type == "Summary by Employee":
        st.subheader("👥 Summary by Employee")
        summary_data = get_settlement_summary_by_employee()
        
        if summary_data:
            import pandas as pd
            df = pd.DataFrame(summary_data)
            
            # Format for display
            display_df = df.copy()
            display_df['base_wage'] = display_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
            display_df['total_advance_taken'] = display_df['total_advance_taken'].apply(lambda x: f"PKR {x:.2f}")
            display_df['total_settlement'] = display_df['total_settlement'].apply(lambda x: f"PKR {x:.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Overall summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Employees", len(df))
            with col2:
                st.metric("Grand Total Settlement", f"PKR {df['total_settlement'].sum():.2f}")
        else:
            st.info("No settlement data available. Start adding entries in the Daily Entry tab.")
    
    else:  # Project-wise Summary
        st.subheader("📁 Project-wise Summary")
        
        # Get all projects summary first
        all_projects_summary = get_all_projects_summary()
        
        if all_projects_summary:
            import pandas as pd
            
            # Show overview of all projects
            st.write("**All Projects Overview:**")
            overview_df = pd.DataFrame(all_projects_summary)
            display_overview = overview_df.copy()
            display_overview['total_advance_taken'] = display_overview['total_advance_taken'].apply(lambda x: f"PKR {x:.2f}")
            display_overview['total_settlement'] = display_overview['total_settlement'].apply(lambda x: f"PKR {x:.2f}")
            st.dataframe(display_overview[['project_id', 'project_name', 'total_employees', 'total_entries', 'total_settlement']], 
                       use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Project selection for detailed view
            projects = get_projects()
            if projects:
                project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] 
                                  for p in projects}
                selected_project = st.selectbox(
                    "Select Project for Detailed View:",
                    options=list(project_options.keys())
                )
                project_id = project_options[selected_project]
                
                # Get project name
                project_name = next((p['project_name'] for p in projects if p['project_id'] == project_id), "Unknown")
                
                st.markdown("---")
                st.write(f"**Detailed Report for: {project_name}**")
                
                # Create two sub-sections using expanders
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("👥 By Employee", expanded=True):
                        st.write(f"**Employee-wise Summary for {project_name}**")
                        employee_summary = get_settlement_by_project_employee(project_id)
                        
                        if employee_summary:
                            emp_df = pd.DataFrame(employee_summary)
                            # Calculate totals before formatting
                            total_emp_settlement = emp_df['total_settlement'].sum()
                            
                            display_emp_df = emp_df.copy()
                            display_emp_df['base_wage'] = display_emp_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
                            display_emp_df['total_advance_taken'] = display_emp_df['total_advance_taken'].apply(lambda x: f"PKR {x:.2f}")
                            display_emp_df['total_settlement'] = display_emp_df['total_settlement'].apply(lambda x: f"PKR {x:.2f}")
                            
                            st.dataframe(display_emp_df[['employee_name', 'total_wage_units', 'base_wage', 'total_advance_taken', 'total_settlement']], 
                                       use_container_width=True, hide_index=True)
                            
                            # Metrics
                            st.metric("Total Employees in Project", len(emp_df))
                            st.metric("Project Employee Settlement", f"PKR {total_emp_settlement:.2f}")
                        else:
                            st.info(f"No wage entries found for {project_name}")
                
                with col2:
                    with st.expander("📊 General Report", expanded=True):
                        st.write(f"**General Report for {project_name}**")
                        general_report = get_settlement_by_project(project_id)
                        
                        if general_report:
                            gen_df = pd.DataFrame(general_report)
                            # Calculate totals before formatting
                            total_gen_settlement = gen_df['calculated_settlement'].sum()
                            total_gen_advance = gen_df['advance_taken'].sum()
                            
                            display_gen_df = gen_df.copy()
                            display_gen_df['date_worked'] = pd.to_datetime(display_gen_df['date_worked']).dt.strftime('%Y-%m-%d')
                            display_gen_df['base_wage'] = display_gen_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
                            display_gen_df['calculated_settlement'] = display_gen_df['calculated_settlement'].apply(lambda x: f"PKR {x:.2f}")
                            
                            st.dataframe(display_gen_df[['date_worked', 'employee_name', 'wage_units', 'advance_taken', 'calculated_settlement']], 
                                       use_container_width=True, hide_index=True)
                            
                            # Summary metrics
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Total Entries", len(gen_df))
                            with col_b:
                                st.metric("Total Settlement", f"PKR {total_gen_settlement:.2f}")
                            with col_c:
                                st.metric("Total Advance", f"PKR {total_gen_advance:.2f}")
                        else:
                            st.info(f"No wage entries found for {project_name}")
            else:
                st.warning("No projects available. Please add projects in the Management tab.")
        else:
            st.info("No project data available. Start adding entries in the Daily Entry tab.")

# ==================== MANAGEMENT TAB ====================
with tab3:
    st.header("⚙️ Management")
    
    st.info("""
    **Instructions:** Use the sections below to add, update, or delete employees and projects.
    Expand each section to access the form.
    """)
    
    # Add New Employee Section
    with st.expander("➕ Add New Employee", expanded=False):
        st.subheader("Employee Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            emp_name = st.text_input("Employee Name:", placeholder="Enter full name")
        
        with col2:
            emp_phone = st.text_input("Phone Number:", placeholder="e.g., 555-0101")
        
        emp_wage = st.number_input("Base Wage (PKR/unit):", min_value=0.0, step=0.25, format="%.2f")
        
        # Show success message if exists
        if st.session_state.employee_success:
            st.success(st.session_state.employee_success)
            st.session_state.employee_success = None  # Clear after showing
        
        if st.button("💾 Add Employee", type="primary", use_container_width=True):
            if not emp_name:
                st.warning("⚠️ Please enter an employee name.")
            elif not emp_phone:
                st.warning("⚠️ Please enter a phone number.")
            elif emp_wage <= 0:
                st.warning("⚠️ Please enter a valid base wage greater than 0.")
            else:
                if add_new_employee(emp_name, emp_phone, emp_wage):
                    st.session_state.employee_success = f"✅ Employee '{emp_name}' added successfully!"
                    st.rerun()
                else:
                    st.error("❌ Failed to add employee. Please check the error message above.")
    
    # Add New Project Section
    with st.expander("➕ Add New Project", expanded=False):
        st.subheader("Project Information")
        
        project_name = st.text_input("Project Name:", placeholder="Enter project name")
        
        # Show success message if exists
        if st.session_state.project_success:
            st.success(st.session_state.project_success)
            st.session_state.project_success = None  # Clear after showing
        
        if st.button("💾 Add Project", type="primary", use_container_width=True):
            if not project_name:
                st.warning("⚠️ Please enter a project name.")
            else:
                if add_new_project(project_name):
                    st.session_state.project_success = f"✅ Project '{project_name}' added successfully!"
                    st.rerun()
                else:
                    st.error("❌ Failed to add project. Please check the error message above.")
    
    # Update Employee Section
    with st.expander("✏️ Update Employee", expanded=False):
        st.subheader("Update Employee Information")
        
        employees = get_employees()
        if employees:
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] 
                              for e in employees}
            selected_emp = st.selectbox(
                "Select Employee to Update:",
                options=list(employee_options.keys())
            )
            employee_id = employee_options[selected_emp]
            
            # Get current employee data
            current_emp = next((e for e in employees if e['employee_id'] == employee_id), None)
            
            if current_emp:
                col1, col2 = st.columns(2)
                
                with col1:
                    updated_name = st.text_input("Employee Name:", value=current_emp['name'], key="update_emp_name")
                
                with col2:
                    updated_phone = st.text_input("Phone Number:", value=current_emp.get('phone', ''), key="update_emp_phone")
                
                updated_wage = st.number_input("Base Wage (PKR/unit):", min_value=0.0, step=0.25, 
                                               value=float(current_emp['base_wage']), format="%.2f", key="update_emp_wage")
                
                # Show success message if exists
                if st.session_state.update_employee_success:
                    st.success(st.session_state.update_employee_success)
                    st.session_state.update_employee_success = None
                
                if st.button("💾 Update Employee", type="primary", use_container_width=True, key="update_emp_btn"):
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
                            st.error("❌ Failed to update employee. Please check the error message above.")
        else:
            st.info("No employees available to update. Please add employees first.")
    
    # Delete Employee Section
    with st.expander("🗑️ Delete Employee", expanded=False):
        st.subheader("Delete Employee")
        
        employees = get_employees()
        if employees:
            employee_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] 
                              for e in employees}
            selected_emp = st.selectbox(
                "Select Employee to Delete:",
                options=list(employee_options.keys()),
                key="delete_emp_select"
            )
            employee_id = employee_options[selected_emp]
            
            # Get employee name for confirmation
            emp_name = next((e['name'] for e in employees if e['employee_id'] == employee_id), "Unknown")
            
            # Show success message if exists
            if st.session_state.delete_employee_success:
                st.success(st.session_state.delete_employee_success)
                st.session_state.delete_employee_success = None
            
            confirm_delete = st.checkbox(f"I confirm I want to delete employee: {emp_name}", key="confirm_delete_emp")
            
            if st.button("🗑️ Delete Employee", type="primary", use_container_width=True, key="delete_emp_btn"):
                if not confirm_delete:
                    st.warning("⚠️ Please confirm deletion by checking the checkbox.")
                else:
                    if delete_employee(employee_id):
                        st.session_state.delete_employee_success = f"✅ Employee '{emp_name}' deleted successfully!"
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete employee. Please check the error message above.")
        else:
            st.info("No employees available to delete.")
    
    # Update Project Section
    with st.expander("✏️ Update Project", expanded=False):
        st.subheader("Update Project Information")
        
        projects = get_projects()
        if projects:
            project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] 
                              for p in projects}
            selected_proj = st.selectbox(
                "Select Project to Update:",
                options=list(project_options.keys()),
                key="update_proj_select"
            )
            project_id = project_options[selected_proj]
            
            # Get current project data
            current_proj = next((p for p in projects if p['project_id'] == project_id), None)
            
            if current_proj:
                updated_project_name = st.text_input("Project Name:", value=current_proj['project_name'], key="update_proj_name")
                
                # Show success message if exists
                if st.session_state.update_project_success:
                    st.success(st.session_state.update_project_success)
                    st.session_state.update_project_success = None
                
                if st.button("💾 Update Project", type="primary", use_container_width=True, key="update_proj_btn"):
                    if not updated_project_name:
                        st.warning("⚠️ Please enter a project name.")
                    else:
                        if update_project(project_id, updated_project_name):
                            st.session_state.update_project_success = f"✅ Project '{updated_project_name}' updated successfully!"
                            st.rerun()
                        else:
                            st.error("❌ Failed to update project. Please check the error message above.")
        else:
            st.info("No projects available to update. Please add projects first.")
    
    # Delete Project Section
    with st.expander("🗑️ Delete Project", expanded=False):
        st.subheader("Delete Project")
        
        projects = get_projects()
        if projects:
            project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] 
                              for p in projects}
            selected_proj = st.selectbox(
                "Select Project to Delete:",
                options=list(project_options.keys()),
                key="delete_proj_select"
            )
            project_id = project_options[selected_proj]
            
            # Get project name for confirmation
            proj_name = next((p['project_name'] for p in projects if p['project_id'] == project_id), "Unknown")
            
            # Show success message if exists
            if st.session_state.delete_project_success:
                st.success(st.session_state.delete_project_success)
                st.session_state.delete_project_success = None
            
            confirm_delete = st.checkbox(f"I confirm I want to delete project: {proj_name}", key="confirm_delete_proj")
            
            if st.button("🗑️ Delete Project", type="primary", use_container_width=True, key="delete_proj_btn"):
                if not confirm_delete:
                    st.warning("⚠️ Please confirm deletion by checking the checkbox.")
                else:
                    if delete_project(project_id):
                        st.session_state.delete_project_success = f"✅ Project '{proj_name}' deleted successfully!"
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete project. Please check the error message above.")
        else:
            st.info("No projects available to delete.")
    
    # Display current data
    st.markdown("---")
    st.subheader("📋 Current Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Employees:**")
        employees = get_employees()
        if employees:
            import pandas as pd
            emp_df = pd.DataFrame(employees)
            st.dataframe(emp_df[['employee_id', 'name', 'phone', 'base_wage']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No employees added yet.")
    
    with col2:
        st.write("**Current Projects:**")
        projects = get_projects()
        if projects:
            import pandas as pd
            proj_df = pd.DataFrame(projects)
            st.dataframe(proj_df, use_container_width=True, hide_index=True)
        else:
            st.info("No projects added yet.")

