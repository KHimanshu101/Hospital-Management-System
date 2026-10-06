import os
import mysql.connector
from config import Config

def init_database():
    print(f"Connecting to MySQL server at {Config.DB_HOST}:{Config.DB_PORT} as user '{Config.DB_USER}'...")
    
    # 1. Connect without selecting database to ensure database exists
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    cursor = conn.cursor()
    
    print(f"Ensuring database '{Config.DB_NAME}' exists...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
    cursor.close()
    conn.close()
    
    # 2. Connect to the target database
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = conn.cursor()
    
    # 3. Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    print(f"Applying schema from '{schema_path}'...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    for statement in schema_sql.split(';'):
        stmt = statement.strip()
        # Skip empty statements and comments/delimiters
        if stmt and not stmt.startswith('--') and not stmt.lower().startswith('use '):
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                print(f"Warning/Error executing DDL statement: {err}")
    
    conn.commit()
    print("Schema applied successfully!")
    
    # 4. Read and execute seed.sql
    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    print(f"Seeding database from '{seed_path}'...")
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_sql = f.read()
    
    for statement in seed_sql.split(';'):
        stmt = statement.strip()
        if stmt and not stmt.startswith('--') and not stmt.lower().startswith('use '):
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                print(f"Warning/Error executing DML statement: {err}")
                
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Database '{Config.DB_NAME}' successfully initialized and seeded with demo data!")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n[ERROR] Database initialization failed: {e}")
        print("Please check your .env configuration and ensure MySQL Server is running.")
