# Banking data assignment

# Project Overview

# Project Structure

├── dags/                           # Airflow DAGs
│ └── banking_dq_dag.py             # Main DAG for data generation and audit
├── src/    
│ ├── generate_data.py              # Script to generate synthetic data using Faker
│ ├── data_quality_standards.py     # Contains DQ check functions
│ └── monitoring_audit.py           # Executes DQ checks and logs output
├── visualization/  
│ └── dashboard.py                  # Streamlit dashboard for DQ results
├── sql/    
│ └── schema_pg.sql                 # SQL schema for PostgreSQL
├── .env                            # Environment variables
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Multi-container Docker setup
└── README.md                       # Project documentation

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



