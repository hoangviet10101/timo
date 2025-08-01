# Banking data assignment

# Project Overview

# Project Structure

banking-data-monitoring/
├── dags/                       # Airflow DAGs
│   └── banking_dq_dag.py
│
├── src/                        # Core Python logic
│   ├── monitoring_audit.py     # Main DQ check script
│   ├── data_quality_checks.py  # All individual check functions
│   └── utils.py                # (optional) helper functions
│
├── dashboard/                  # Streamlit dashboard
│   ├── dashboard.py            # Main Streamlit app
│   └── components.py           # Optional reusable UI components
│
├── sql/                        # Reusable SQL queries (optional)
│   └── init_schema.sql         # Table schema
│
├── tests/                      # Unit tests (optional)
│   └── test_data_quality.py
│
├── .env.example                # Example env vars (DON’T commit your real `.env`)
├── .gitignore
├── requirements.txt            # All Python dependencies
├── README.md                   # Project description
├── LICENSE                     # (optional) open source license
└── setup.sh                    # (optional) helper script to set up local env


# Setup Instructions
## Requirements

Python 3.8+
Docker
virtual environment (venv)

# Run the project
1. Start docker containers
docker compose up -d --build

2. Load schema into database
docker exec -it postgres bash
psql -U airflow -d {database name} -f /sql/schema_pg.sql # Here I used "timo"

This will create the tables in db

3. Run DAG for data generation and data quality checks
Go to Airflow at http://localhost:8080
Logs are available for each task 

4. Streamlit
Activate venv first, install all requirements then run streamlit

python -m venv venv # Create virtual environment
.\venv\Scripts\activate

If error like this: 
venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see 
about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:1
+ .\venv\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess

run Powershell with admin, type:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

then activate again.
Remember to install all requirements:
pip install -r requirements.txt

Finally, run this:
streamlit run visualization/dashboard.py



