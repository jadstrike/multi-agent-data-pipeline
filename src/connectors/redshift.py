import psycopg2
import pandas as pd

def connect(host: str, port: int, database: str, user: str, password: str):
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    return conn

def list_tables(host: str, port: int, database: str, user: str, password: str) -> list:
    conn = connect(host, port, database, user, password)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

def fetch_table(host: str, port: int, database: str, user: str, password: str, table: str, limit: int = 1000) -> pd.DataFrame:
    conn = connect(host, port, database, user, password)
    cursor = conn.cursor()

    try:
        # Validate table exists to prevent SQL injection
        valid_tables = list_tables(host, port, database, user, password)
        if table not in valid_tables:
            raise ValueError(f"Table '{table}' not found in database. Available tables: {', '.join(valid_tables)}")

        cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        conn.close()
