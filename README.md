# Contractor App V1

A comprehensive wage management system built with Streamlit and MySQL for managing employees, projects, and wage entries.

## Features

- **Employee Management**: Create, Read, Update, and Delete employees
- **Project Management**: Create, Read, Update, and Delete projects
- **Wage Entry System**: Record daily wage entries with project and employee tracking
- **Settlement Reports**: 
  - Detailed settlement reports
  - Employee-wise summaries
  - Project-wise summaries with employee breakdowns
- **Data Preservation**: Wage entries are preserved even when employees or projects are deleted

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **Libraries**: 
  - mysql-connector-python
  - pandas
  - numpy
  - matplotlib

## Setup Instructions

### Prerequisites
- Python 3.x
- MySQL Server
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/Contractor_APP_V1.git
cd Contractor_APP_V1
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install streamlit pandas numpy matplotlib mysql-connector-python
```

4. Set up the database:
   - Update MySQL connection credentials in `init_db.py`, `database_logic.py`, and `app.py`
   - Run the database initialization:
   ```bash
   python init_db.py
   ```

5. Run the application:
```bash
streamlit run app.py
```

## Database Schema

- **employees**: employee_id, name, phone, base_wage
- **projects**: project_id, project_name
- **wage_entries**: entry_id, project_id, employee_id, date_worked, wage_units, advance_taken

## Project Structure

```
Contractor_APP_V1/
├── app.py                  # Main Streamlit application
├── database_logic.py       # Database operations (CRUD)
├── init_db.py             # Database initialization script
├── fix_database.py        # Database schema fix utility
├── remove_cascade_delete.py # Migration script for removing cascade deletes
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Usage

1. **Management Tab**: Add, update, or delete employees and projects
2. **Daily Entry Tab**: Record wage entries for employees working on projects
3. **Reports Tab**: View detailed settlement reports and summaries

## Notes

- All currency values are displayed in PKR (Pakistani Rupee)
- Wage entries are preserved when employees or projects are deleted (foreign keys set to NULL)
- All database operations use parameterized queries for security

## License

Private Repository

