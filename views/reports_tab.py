"""
Reports Tab View — Tab 2
Handles all settlement report displays.
"""

import streamlit as st
import pandas as pd
from db.projects import get_projects
from db.reports import (
    get_settlement_report,
    get_settlement_summary_by_employee,
    get_settlement_by_project,
    get_settlement_by_project_employee,
    get_all_projects_summary,
    get_expense_summary_by_project
)


def render():
    st.header("📊 Settlement Reports")
    st.info("""
    **Instructions:** View detailed settlement reports and summaries.
    The reports show calculated settlements: (wage_units × base_wage) - advance_taken
    """)

    report_type = st.radio(
        "Select Report Type:",
        ["Detailed Report", "Summary by Employee", "Project-wise Summary", "Expense Summary By Project"],
        horizontal=True
    )

    if report_type == "Detailed Report":
        st.subheader("📋 Detailed Settlement Report")
        report_data = get_settlement_report()

        if report_data:
            df = pd.DataFrame(report_data)
            total_settlement = df['calculated_settlement'].sum()
            total_advance = df['advance_taken'].sum()

            display_df = df.copy()
            display_df['date_worked'] = pd.to_datetime(display_df['date_worked']).dt.strftime('%Y-%m-%d')
            display_df['base_wage'] = display_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
            display_df['calculated_settlement'] = display_df['calculated_settlement'].apply(lambda x: f"PKR {x:.2f}")

            st.dataframe(display_df, width='stretch', hide_index=True)

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
            df = pd.DataFrame(summary_data)
            display_df = df.copy()
            display_df['base_wage'] = display_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
            display_df['total_advance_taken'] = display_df['total_advance_taken'].apply(lambda x: f"PKR {x:.2f}")
            display_df['total_settlement'] = display_df['total_settlement'].apply(lambda x: f"PKR {x:.2f}")

            st.dataframe(display_df, width='stretch', hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Employees", len(df))
            with col2:
                st.metric("Grand Total Settlement", f"PKR {df['total_settlement'].sum():.2f}")
        else:
            st.info("No settlement data available.")

    elif report_type == "Project-wise Summary":  # Project-wise Summary
        st.subheader("📁 Project-wise Summary")
        all_projects_summary = get_all_projects_summary()

        if all_projects_summary:
            st.write("**All Projects Overview:**")
            overview_df = pd.DataFrame(all_projects_summary)
            display_overview = overview_df.copy()
            display_overview = display_overview.rename(columns={
    "total_advance_taken": "total_advance_given"  # ← rename only for display
})
            display_overview['total_advance_given'] = display_overview['total_advance_given'].apply(lambda x: f"PKR {x:.2f}")
            display_overview['total_settlement'] = display_overview['total_settlement'].apply(lambda x: f"PKR {x:.2f}")
            st.dataframe(
                display_overview[['project_id', 'project_name', 'total_employees', 'total_entries', 'total_settlement']],
                width='stretch', hide_index=True
            )

            st.markdown("---")

            projects = get_projects()
            if projects:
                project_options = {f"{p['project_id']} - {p['project_name']}": p['project_id'] for p in projects}
                selected_project = st.selectbox("Select Project for Detailed View:", options=list(project_options.keys()))
                project_id = project_options[selected_project]
                project_name = next((p['project_name'] for p in projects if p['project_id'] == project_id), "Unknown")

                st.markdown("---")
                st.write(f"**Detailed Report for: {project_name}**")

                col1, col2 = st.columns(2)

                with col1:
                    with st.expander("👥 By Employee", expanded=True):
                        st.write(f"**Employee-wise Summary for {project_name}**")
                        employee_summary = get_settlement_by_project_employee(project_id)

                        if employee_summary:
                            emp_df = pd.DataFrame(employee_summary)
                            total_emp_settlement = emp_df['total_settlement'].sum()
                            display_emp_df = emp_df.copy()
                            display_emp_df = display_emp_df.rename(columns={
    "total_advance_taken": "total_advance_given"  # ← rename only for display
})
                            display_emp_df['base_wage'] = display_emp_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
                            display_emp_df['total_advance_given'] = display_emp_df['total_advance_given'].apply(lambda x: f"PKR {x:.2f}")
                            display_emp_df['total_settlement'] = display_emp_df['total_settlement'].apply(lambda x: f"PKR {x:.2f}")
                            st.dataframe(
                                display_emp_df[['employee_name', 'total_wage_units', 'base_wage', 'total_advance_given', 'total_settlement']],
                                width='stretch', hide_index=True
                            )
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
                            total_gen_settlement = gen_df['calculated_settlement'].sum()
                            total_gen_advance = gen_df['advance_taken'].sum()
                            display_gen_df = gen_df.copy()
                            display_gen_df['date_worked'] = pd.to_datetime(display_gen_df['date_worked']).dt.strftime('%Y-%m-%d')
                            display_gen_df['base_wage'] = display_gen_df['base_wage'].apply(lambda x: f"PKR {x:.2f}")
                            display_gen_df['calculated_settlement'] = display_gen_df['calculated_settlement'].apply(lambda x: f"PKR {x:.2f}")
                            st.dataframe(
                                display_gen_df[['date_worked', 'employee_name', 'wage_units', 'advance_taken', 'calculated_settlement']],
                                width='stretch', hide_index=True
                            )
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
                st.warning("No projects available.")
        else:
            st.info("No project data available. Start adding entries in the Daily Entry tab.")
    else:  # Expense Summary
        st.subheader("🧾 Expense Summary by Project")
        expense_data = get_expense_summary_by_project()
 
        if expense_data:
            df = pd.DataFrame(expense_data)
            display_df = df.copy()
            display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"PKR {x:.2f}")
 
            st.dataframe(
                display_df[['project_id', 'project_name', 'total_items', 'total_amount']],
                width='stretch',
                hide_index=True
            )
 
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Projects with Expenses", len(df))
            with col2:
                st.metric("Grand Total Expenses", f"PKR {df['total_amount'].sum():.2f}")
        else:
            st.info("No expense entries found. Start adding expenses in the Daily Entry tab.")
 