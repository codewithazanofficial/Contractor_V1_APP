import mysql.connector
from mysql.connector import Error


def get_connection(database='companydata', host='localhost', user='root', password='new_password'):
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def remove_cascade_delete():
    """Remove cascade delete constraints and allow wage entries to persist when employees/projects are deleted."""
    connection = get_connection()
    
    if not connection:
        print("Failed to connect to database")
        return
    
    try:
        cursor = connection.cursor()
        
        print("Removing foreign key constraints with CASCADE DELETE...")
        
        # Drop existing foreign key constraints
        try:
            cursor.execute("ALTER TABLE wage_entries DROP FOREIGN KEY wage_entries_ibfk_1")
            print("SUCCESS: Dropped foreign key constraint for project_id")
        except Error as e:
            print(f"Note: Could not drop project_id constraint (may have different name): {e}")
            # Try alternative constraint names
            try:
                cursor.execute("ALTER TABLE wage_entries DROP FOREIGN KEY wage_entries_ibfk_2")
            except:
                pass
        
        try:
            cursor.execute("ALTER TABLE wage_entries DROP FOREIGN KEY wage_entries_ibfk_2")
            print("SUCCESS: Dropped foreign key constraint for employee_id")
        except Error as e:
            print(f"Note: Could not drop employee_id constraint (may have different name): {e}")
        
        # Get actual constraint names
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'companydata' 
            AND TABLE_NAME = 'wage_entries' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        constraints = cursor.fetchall()
        
        # Drop all foreign key constraints
        for constraint in constraints:
            constraint_name = constraint[0]
            try:
                cursor.execute(f"ALTER TABLE wage_entries DROP FOREIGN KEY {constraint_name}")
                print(f"SUCCESS: Dropped foreign key constraint: {constraint_name}")
            except Error as e:
                print(f"Note: Could not drop constraint {constraint_name}: {e}")
        
        # Make foreign key columns nullable so they can be set to NULL when parent is deleted
        print("\nMaking foreign key columns nullable...")
        cursor.execute("ALTER TABLE wage_entries MODIFY COLUMN project_id INT NULL")
        print("SUCCESS: Made project_id nullable")
        
        cursor.execute("ALTER TABLE wage_entries MODIFY COLUMN employee_id INT NULL")
        print("SUCCESS: Made employee_id nullable")
        
        # Add new foreign keys with ON DELETE SET NULL
        print("\nAdding new foreign key constraints with ON DELETE SET NULL...")
        cursor.execute("""
            ALTER TABLE wage_entries 
            ADD CONSTRAINT fk_wage_entries_project 
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL
        """)
        print("SUCCESS: Added foreign key for project_id with ON DELETE SET NULL")
        
        cursor.execute("""
            ALTER TABLE wage_entries 
            ADD CONSTRAINT fk_wage_entries_employee 
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL
        """)
        print("SUCCESS: Added foreign key for employee_id with ON DELETE SET NULL")
        
        connection.commit()
        print("\nSUCCESS: Successfully removed cascade delete constraints!")
        print("Wage entries will now be preserved when employees or projects are deleted.")
        print("The employee_id and project_id will be set to NULL in related wage entries.")
        
        cursor.close()
        
    except Error as e:
        print(f"Error: {e}")
        if connection.is_connected():
            connection.rollback()
    finally:
        if connection.is_connected():
            connection.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Removing CASCADE DELETE Constraints")
    print("=" * 60)
    remove_cascade_delete()

