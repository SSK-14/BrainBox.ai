import pymysql, json
from src.modules.model import text_embedding
from src.database.main import create_connection

TIME_TO_LIVE = 36000

def create_cache_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cache (
        id INT PRIMARY KEY AUTO_INCREMENT,
        key_str VARCHAR(255) UNIQUE NOT NULL,
        key_vec JSON NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        ttl TIMESTAMP GENERATED ALWAYS AS (created_at + INTERVAL %s SECOND) VIRTUAL
    ) ENGINE=InnoDB;
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql, (TIME_TO_LIVE,))
            connection.commit()
    finally:
        connection.close()

def delete_expired_entries():
    delete_sql = "DELETE FROM cache WHERE NOW() > ttl"
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(delete_sql)
            connection.commit()
            return {'message': 'Expired entries deleted'}
    finally:
        connection.close()

create_cache_table()
delete_expired_entries()

def set_cache(key: str, value: str):
    key_vec = text_embedding(key)
    insert_sql = "INSERT INTO cache (key_str, key_vec, value) VALUES (%s, %s, %s)"
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(insert_sql, (key, json.dumps(key_vec), value))
            connection.commit()
            return {'message': 'Cache has been set'}
    except Exception as e:
        connection.rollback()
        return {'error': str(e)}
    finally:
        connection.close()

def get_cache(key: str, max_distance: float = 0.1):
    key_vec = text_embedding(key)
    fetch_sql = """
    SELECT key_str, value, 
           JSON_EXTRACT(key_vec, '$[0]') - %s AS distance
    FROM cache
    ORDER BY distance ASC
    LIMIT 1;
    """
    connection = create_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(fetch_sql, (json.dumps(key_vec[0]),))
            result = cursor.fetchone()
            if result and result['distance'] <= max_distance:
                return result['key_str'], result['value']
            else:
                return None, None
    finally:
        connection.close()

def delete_cache(key: str):
    delete_sql = "DELETE FROM cache WHERE key_str = %s"
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(delete_sql, (key,))
            connection.commit()
            return {'message': 'Cache entry deleted'}
    finally:
        connection.close()
