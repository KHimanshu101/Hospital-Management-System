import mysql.connector
from config import Config

def migrate_database():
    print(f"Connecting to MySQL database '{Config.DB_NAME}' at {Config.DB_HOST}:{Config.DB_PORT}...")
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = conn.cursor()
    
    # 1. Add email column to users if not exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'email'
    """, (Config.DB_NAME,))
    has_email = cursor.fetchone()[0] > 0
    
    if not has_email:
        print("Adding 'email' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100) UNIQUE NULL AFTER username;")
        # Backfill default emails for seeded users if null
        cursor.execute("UPDATE users SET email = CONCAT(username, '@carepoint.org') WHERE email IS NULL;")
        conn.commit()
        print("Column 'email' added and backfilled successfully.")
    else:
        print("Column 'email' already exists in 'users' table.")
        
    # 2. Create password_resets table if not exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'password_resets'
    """, (Config.DB_NAME,))
    has_pw_resets = cursor.fetchone()[0] > 0
    
    if not has_pw_resets:
        print("Creating 'password_resets' table...")
        cursor.execute("""
            CREATE TABLE password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                used_at DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_pwreset_user FOREIGN KEY (user_id) 
                    REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
                INDEX idx_pwreset_token (token_hash),
                INDEX idx_pwreset_user_exp (user_id, expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        print("Table 'password_resets' created successfully.")
    else:
        print("Table 'password_resets' already exists.")
        
    cursor.close()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"Migration notice/error: {e}")
