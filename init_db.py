import mysql.connector
from mysql.connector import Error
from datetime import date


def create_connection(host='localhost', user='root', password='new_password'):
    """Create a connection to MySQL server."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection, database_name='companydata'):
    """Create the database if it doesn't exist."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created or already exists")
        cursor.execute(f"USE {database_name}")
        print(f"Using database '{database_name}'")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def create_tables(connection):
    """Create all required tables with AUTO_INCREMENT = 1000."""
    try:
        cursor = connection.cursor()
        
        # Create projects table
        create_projects_table = """
        CREATE TABLE IF NOT EXISTS projects (
            project_id INT AUTO_INCREMENT PRIMARY KEY,
            project_name VARCHAR(255) NOT NULL
        ) AUTO_INCREMENT = 1000
        """
        cursor.execute(create_projects_table)
        print("Table 'projects' created successfully")
        
        # Create employees table
        create_employees_table = """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            base_wage FLOAT NOT NULL
        ) AUTO_INCREMENT = 1000
        """
        cursor.execute(create_employees_table)
        print("Table 'employees' created successfully")
        
        # Create wage_entries table with foreign keys
        # Note: Foreign keys use ON DELETE SET NULL to preserve wage entries when employees/projects are deleted
        create_wage_entries_table = """
        CREATE TABLE IF NOT EXISTS wage_entries (
            entry_id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NULL,
            employee_id INT NULL,
            date_worked DATE NOT NULL,
            wage_units FLOAT NOT NULL,
            advance_taken INT DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL
        ) AUTO_INCREMENT = 1000
        """
        cursor.execute(create_wage_entries_table)
        print("Table 'wage_entries' created successfully")
        
        connection.commit()
        cursor.close()
        print("All tables created successfully")
        
    except Error as e:
        print(f"Error creating tables: {e}")


def seed_database(connection):
    """Seed the database with 2 sample projects and 2 sample employees."""
    try:
        cursor = connection.cursor()
        
        # Insert sample projects
        projects_data = [
            ("Website Redesign",),
            ("Mobile App Development",)
        ]
        
        insert_project = "INSERT INTO projects (project_name) VALUES (%s)"
        cursor.executemany(insert_project, projects_data)
        print("Inserted 2 sample projects")
        
        # Insert sample employees
        employees_data = [
            ("John Doe", "555-0101", 25.50),
            ("Jane Smith", "555-0102", 30.75)
        ]
        
        insert_employee = "INSERT INTO employees (name, phone, base_wage) VALUES (%s, %s, %s)"
        cursor.executemany(insert_employee, employees_data)
        print("Inserted 2 sample employees")
        
        connection.commit()
        cursor.close()
        print("Database seeded successfully")
        
    except Error as e:
        print(f"Error seeding database: {e}")


def main():
    """Main function to initialize the database."""
    # Update these connection parameters as needed
    host = 'localhost'
    user = 'root'
    password = 'new_password'  # Update with your MySQL password if required
    
    connection = create_connection(host, user, password)
    
    if connection:
        try:
            create_database(connection, 'companydata')
            create_tables(connection)
            seed_database(connection)
            print("\nDatabase initialization completed successfully!")
            
        except Error as e:
            print(f"Error during initialization: {e}")
        finally:
            if connection.is_connected():
                connection.close()
                print("MySQL connection closed")


if __name__ == "__main__":
    main()

