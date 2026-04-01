import psycopg2
from psycopg2.extras import RealDictCursor
from settings import settings
import logging

db_config = settings.get("database", {})

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=db_config.get("host", "94.159.111.243"),
            port=db_config.get("port", "5432"),
            dbname=db_config.get("name", "mobile_data"),
            user=db_config.get("user", "mobile_data_user"),
            password=settings.get("db_password", db_config.get("password", "")),
            cursor_factory=RealDictCursor
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        raise

def init_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(50) PRIMARY KEY,
                    nickname VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    time_registration DOUBLE PRECISION NOT NULL
                );
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mobile_data (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
                    mobile_network_data_list JSONB,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    altitude DOUBLE PRECISION,
                    time BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cur.execute("CREATE INDEX IF NOT EXISTS idx_mobile_data_user_time ON mobile_data(user_id, time DESC NULLS LAST);")
            
            cur.execute("CREATE INDEX IF NOT EXISTS idx_mobile_data_user_id ON mobile_data(user_id);")

        conn.close()
    except Exception as e:
        logging.error(f"Warning: Could not initialize database: {e}")

init_db()