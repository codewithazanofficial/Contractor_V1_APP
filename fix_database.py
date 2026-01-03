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


def check_table_structure(connection, table_name):
    """Check the structure of a table."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\n{table_name} table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        cursor.close()
        return columns
    except Error as e:
        print(f"Error checking {table_name}: {e}")
        return None


def fix_employees_table(connection):
    """Fix the employees table by adding missing columns."""
    try:
        cursor = connection.cursor()
        
        # Check if phone column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'companydata' 
            AND TABLE_NAME = 'employees' 
            AND COLUMN_NAME = 'phone'
        """)
        phone_exists = cursor.fetchone()[0] > 0
        
        if not phone_exists:
            print("Adding 'phone' column to employees table...")
            cursor.execute("ALTER TABLE employees ADD COLUMN phone VARCHAR(20) AFTER name")
            connection.commit()
            print("SUCCESS: 'phone' column added successfully")
        else:
            print("OK: 'phone' column already exists")
        
        # Check if base_wage column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'companydata' 
            AND TABLE_NAME = 'employees' 
            AND COLUMN_NAME = 'base_wage'
        """)
        base_wage_exists = cursor.fetchone()[0] > 0
        
        if not base_wage_exists:
            print("Adding 'base_wage' column to employees table...")
            cursor.execute("ALTER TABLE employees ADD COLUMN base_wage FLOAT NOT NULL DEFAULT 0 AFTER phone")
            connection.commit()
            print("SUCCESS: 'base_wage' column added successfully")
        else:
            print("OK: 'base_wage' column already exists")
            # Check if base_wage is INT and needs to be changed to FLOAT
            cursor.execute("""
                SELECT DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'companydata' 
                AND TABLE_NAME = 'employees' 
                AND COLUMN_NAME = 'base_wage'
            """)
            base_wage_type = cursor.fetchone()[0]
            if base_wage_type == 'int':
                print("Converting 'base_wage' from INT to FLOAT...")
                cursor.execute("ALTER TABLE employees MODIFY COLUMN base_wage FLOAT NOT NULL")
                connection.commit()
                print("SUCCESS: 'base_wage' converted to FLOAT")
            else:
                print(f"OK: 'base_wage' is already {base_wage_type.upper()}")
        
        # Check if employee_id column exists (rename id to employee_id if needed)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'companydata' 
            AND TABLE_NAME = 'employees' 
            AND COLUMN_NAME = 'employee_id'
        """)
        employee_id_exists = cursor.fetchone()[0] > 0
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'companydata' 
            AND TABLE_NAME = 'employees' 
            AND COLUMN_NAME = 'id'
        """)
        id_exists = cursor.fetchone()[0] > 0
        
        if id_exists and not employee_id_exists:
            print("Renaming 'id' column to 'employee_id'...")
            # First, drop foreign key constraints that reference this column
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("ALTER TABLE employees CHANGE COLUMN id employee_id INT AUTO_INCREMENT")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                connection.commit()
                print("SUCCESS: Column renamed from 'id' to 'employee_id'")
            except Error as e:
                print(f"Note: Could not rename column (may already be correct or have constraints): {e}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        else:
            print("OK: 'employee_id' column already exists or 'id' column doesn't exist")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"Error fixing employees table: {e}")
        return False


def fix_all_tables(connection):
    """Ensure all tables have the correct structure."""
    try:
        cursor = connection.cursor()
        
        # Check and fix employees table
        print("\n=== Fixing employees table ===")
        fix_employees_table(connection)
        
        # Check projects table
        print("\n=== Checking projects table ===")
        check_table_structure(connection, 'projects')
        
        # Check wage_entries table
        print("\n=== Checking wage_entries table ===")
        check_table_structure(connection, 'wage_entries')
        
        # Verify AUTO_INCREMENT settings
        print("\n=== Checking AUTO_INCREMENT settings ===")
        cursor.execute("SHOW TABLE STATUS WHERE Name = 'projects'")
        projects_status = cursor.fetchone()
        print(f"projects AUTO_INCREMENT: {projects_status[10]}")
        
        cursor.execute("SHOW TABLE STATUS WHERE Name = 'employees'")
        employees_status = cursor.fetchone()
        print(f"employees AUTO_INCREMENT: {employees_status[10]}")
        
        cursor.execute("SHOW TABLE STATUS WHERE Name = 'wage_entries'")
        wage_entries_status = cursor.fetchone()
        print(f"wage_entries AUTO_INCREMENT: {wage_entries_status[10]}")
        
        cursor.close()
        
    except Error as e:
        print(f"Error fixing tables: {e}")


def main():
    """Main function to examine and fix the database."""
    connection = get_connection()
    
    if connection:
        try:
            print("=== Current Database Structure ===")
            check_table_structure(connection, 'employees')
            check_table_structure(connection, 'projects')
            check_table_structure(connection, 'wage_entries')
            
            print("\n=== Fixing Database Structure ===")
            fix_all_tables(connection)
            
            print("\n=== Final Database Structure ===")
            check_table_structure(connection, 'employees')
            check_table_structure(connection, 'projects')
            check_table_structure(connection, 'wage_entries')
            
            print("\nSUCCESS: Database structure check and fix completed!")
            
        except Error as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                connection.close()
                print("\nMySQL connection closed")
    else:
        print("Failed to connect to database. Please check your connection settings.")


if __name__ == "__main__":
    main()

