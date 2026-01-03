"""
Database Logic Module - Internal API

All database operations use parameterized queries for security.
"""

import mysql.connector
from mysql.connector import Error
from datetime import date
from typing import List, Dict, Optional, Tuple


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
        print(f"Error connecting to MySQL: {e}")
        return None


def get_projects() -> List[Dict[str, any]]:
    """
    Retrieve all projects with their IDs and names.
    
    Returns:
        List of dictionaries with 'project_id' and 'project_name' keys
    """
    connection = get_connection()
    projects = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT project_id, project_name FROM projects ORDER BY project_id"
            cursor.execute(query)
            projects = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching projects: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return projects


def get_employees() -> List[Dict[str, any]]:
    """
    Retrieve all employees with their IDs and names.
    
    Returns:
        List of dictionaries with 'employee_id', 'name', 'phone', and 'base_wage' keys
    """
    connection = get_connection()
    employees = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT employee_id, name, phone, base_wage FROM employees ORDER BY employee_id"
            cursor.execute(query)
            employees = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching employees: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return employees


def add_wage_entry(project_id: int, employee_id: int, date_worked: date, 
                   wage_units: float, advance_taken: int = 0) -> bool:
    """
    Add a new wage entry to the database.
    
    Args:
        project_id: ID of the project
        employee_id: ID of the employee
        date_worked: Date when work was performed
        wage_units: Number of wage units worked
        advance_taken: Advance amount taken (default: 0)
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    success = False
    
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO wage_entries 
                (project_id, employee_id, date_worked, wage_units, advance_taken)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (project_id, employee_id, date_worked, wage_units, advance_taken)
            cursor.execute(query, values)
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            print(f"Error adding wage entry: {e}")
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    
    return success


def get_settlement_report() -> List[Dict[str, any]]:
    """
    Generate a settlement report by joining all three tables.
    Calculates: (wage_units * base_wage) - advance_taken per employee.
    
    Returns:
        List of dictionaries containing:
        - employee_id
        - employee_name
        - project_id
        - project_name
        - date_worked
        - wage_units
        - base_wage
        - advance_taken
        - calculated_settlement (wage_units * base_wage - advance_taken)
    """
    connection = get_connection()
    report = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.employee_id,
                    e.name AS employee_name,
                    p.project_id,
                    p.project_name,
                    w.date_worked,
                    w.wage_units,
                    e.base_wage,
                    w.advance_taken,
                    (w.wage_units * e.base_wage) - w.advance_taken AS calculated_settlement
                FROM wage_entries w
                INNER JOIN employees e ON w.employee_id = e.employee_id
                INNER JOIN projects p ON w.project_id = p.project_id
                ORDER BY e.employee_id, w.date_worked
            """
            cursor.execute(query)
            report = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error generating settlement report: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return report


def get_settlement_summary_by_employee() -> List[Dict[str, any]]:
    """
    Get a summary settlement report grouped by employee.
    Calculates total settlement per employee across all projects.
    
    Returns:
        List of dictionaries containing:
        - employee_id
        - employee_name
        - total_wage_units
        - base_wage
        - total_advance_taken
        - total_settlement
    """
    connection = get_connection()
    summary = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.employee_id,
                    e.name AS employee_name,
                    SUM(w.wage_units) AS total_wage_units,
                    e.base_wage,
                    SUM(w.advance_taken) AS total_advance_taken,
                    SUM((w.wage_units * e.base_wage) - w.advance_taken) AS total_settlement
                FROM wage_entries w
                INNER JOIN employees e ON w.employee_id = e.employee_id
                GROUP BY e.employee_id, e.name, e.base_wage
                ORDER BY e.employee_id
            """
            cursor.execute(query)
            summary = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error generating settlement summary: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return summary


def get_settlement_by_project(project_id: int) -> List[Dict[str, any]]:
    """
    Get a general settlement report for a specific project.
    
    Args:
        project_id: ID of the project
    
    Returns:
        List of dictionaries containing all wage entries for the project with calculations
    """
    connection = get_connection()
    report = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.employee_id,
                    e.name AS employee_name,
                    p.project_id,
                    p.project_name,
                    w.date_worked,
                    w.wage_units,
                    e.base_wage,
                    w.advance_taken,
                    (w.wage_units * e.base_wage) - w.advance_taken AS calculated_settlement
                FROM wage_entries w
                INNER JOIN employees e ON w.employee_id = e.employee_id
                INNER JOIN projects p ON w.project_id = p.project_id
                WHERE p.project_id = %s
                ORDER BY w.date_worked, e.employee_id
            """
            cursor.execute(query, (project_id,))
            report = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error generating project settlement report: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return report


def get_settlement_by_project_employee(project_id: int) -> List[Dict[str, any]]:
    """
    Get settlement summary by employee for a specific project.
    
    Args:
        project_id: ID of the project
    
    Returns:
        List of dictionaries containing employee-wise summary for the project
    """
    connection = get_connection()
    summary = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.employee_id,
                    e.name AS employee_name,
                    p.project_id,
                    p.project_name,
                    SUM(w.wage_units) AS total_wage_units,
                    e.base_wage,
                    SUM(w.advance_taken) AS total_advance_taken,
                    SUM((w.wage_units * e.base_wage) - w.advance_taken) AS total_settlement
                FROM wage_entries w
                INNER JOIN employees e ON w.employee_id = e.employee_id
                INNER JOIN projects p ON w.project_id = p.project_id
                WHERE p.project_id = %s
                GROUP BY e.employee_id, e.name, e.base_wage, p.project_id, p.project_name
                ORDER BY e.employee_id
            """
            cursor.execute(query, (project_id,))
            summary = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error generating project employee summary: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return summary


def get_all_projects_summary() -> List[Dict[str, any]]:
    """
    Get summary settlement report for all projects.
    Shows general statistics per project.
    
    Returns:
        List of dictionaries containing project-wise summaries
    """
    connection = get_connection()
    summary = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    p.project_id,
                    p.project_name,
                    COUNT(DISTINCT w.employee_id) AS total_employees,
                    COUNT(w.entry_id) AS total_entries,
                    SUM(w.wage_units) AS total_wage_units,
                    SUM(w.advance_taken) AS total_advance_taken,
                    SUM((w.wage_units * e.base_wage) - w.advance_taken) AS total_settlement
                FROM wage_entries w
                INNER JOIN employees e ON w.employee_id = e.employee_id
                INNER JOIN projects p ON w.project_id = p.project_id
                GROUP BY p.project_id, p.project_name
                ORDER BY p.project_id
            """
            cursor.execute(query)
            summary = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error generating all projects summary: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    return summary


def update_employee(employee_id: int, name: str, phone: str, base_wage: float) -> bool:
    """
    Update an existing employee's information.
    
    Args:
        employee_id: ID of the employee to update
        name: Updated employee name
        phone: Updated phone number
        base_wage: Updated base wage
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    success = False
    
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                UPDATE employees 
                SET name = %s, phone = %s, base_wage = %s
                WHERE employee_id = %s
            """
            values = (name, phone, base_wage, employee_id)
            cursor.execute(query, values)
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            print(f"Error updating employee: {e}")
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    
    return success


def delete_employee(employee_id: int) -> bool:
    """
    Delete an employee from the database.
    Note: Related wage entries will be preserved with employee_id set to NULL.
    
    Args:
        employee_id: ID of the employee to delete
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    success = False
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM employees WHERE employee_id = %s"
            values = (employee_id,)
            cursor.execute(query, values)
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            print(f"Error deleting employee: {e}")
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    
    return success


def update_project(project_id: int, project_name: str) -> bool:
    """
    Update an existing project's name.
    
    Args:
        project_id: ID of the project to update
        project_name: Updated project name
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    success = False
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE projects SET project_name = %s WHERE project_id = %s"
            values = (project_name, project_id)
            cursor.execute(query, values)
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            print(f"Error updating project: {e}")
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    
    return success


def delete_project(project_id: int) -> bool:
    """
    Delete a project from the database.
    Note: Related wage entries will be preserved with project_id set to NULL.
    
    Args:
        project_id: ID of the project to delete
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    success = False
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM projects WHERE project_id = %s"
            values = (project_id,)
            cursor.execute(query, values)
            connection.commit()
            success = True
            cursor.close()
        except Error as e:
            print(f"Error deleting project: {e}")
            if connection.is_connected():
                connection.rollback()
        finally:
            if connection.is_connected():
                connection.close()
    
    return success

