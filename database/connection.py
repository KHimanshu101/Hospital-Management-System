import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool holder
_db_pool = None

def get_db_pool():
    global _db_pool
    if _db_pool is None:
        try:
            _db_pool = pooling.MySQLConnectionPool(
                pool_name="carepoint_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False
            )
            logger.info(f"Database connection pool initialized for DB '{Config.DB_NAME}' at {Config.DB_HOST}:{Config.DB_PORT}")
        except Error as err:
            logger.error(f"Error creating MySQL connection pool: {err}")
            raise err
    return _db_pool

def get_direct_connection(database=None):
    """Obtain a direct non-pooled connection, useful for setup scripts or testing."""
    target_db = database if database is not None else Config.DB_NAME
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=target_db
    )

@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """
    Context manager providing a database cursor and handling connection lifecycle,
    transactions (commit/rollback), and resource cleanup.
    """
    conn = None
    cursor = None
    try:
        pool = get_db_pool()
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor
        if commit:
            conn.commit()
    except Error as err:
        if conn and conn.is_connected():
            conn.rollback()
        logger.error(f"Database operation failed: {err}")
        raise err
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def check_db_connection():
    """Verify database connection health."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 AS alive")
            result = cursor.fetchone()
            return result is not None and result.get('alive') == 1
    except Exception as e:
        logger.warning(f"Database connectivity check failed: {e}")
        return False
