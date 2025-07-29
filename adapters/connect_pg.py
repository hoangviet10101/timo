import psycopg2

conn = psycopg2.connect(
    dbname='timo',
    user='airflow',
    password='airflow',
    host='localhost',
    port='5432'
)

cursor = conn.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
print(cursor.fetchall())

cursor.close()
conn.close()
