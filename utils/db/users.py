from typing import Dict, List, Optional, Union, Iterable
from cachetools import cached, TTLCache
from beartype import beartype
from threading import Lock
import shortuuid
import time
import logging

from utils.db.cache_manager import users_cache, clear_cache
from utils.db.connection import get_db_connection

def _generate_user_id() -> str:
    return f"user_{shortuuid.uuid()}"

@cached(users_cache["get_users"])
@beartype
def get_users() -> Dict[str, Dict[str, Union[str, List[str]]]]:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, nickname, password_hash, time_registration, email, full_name FROM users")
            rows = cur.fetchall()
            users = {}
            for row in rows:
                user_dict = {
                    "id": row['id'],
                    "nickname": row['nickname'],
                    "password_hash": row['password_hash'],
                    "time_registration": row['time_registration']
                }
                if row.get('email'):
                    user_dict['email'] = row['email']
                if row.get('full_name'):
                    user_dict['full_name'] = row['full_name']
                users[row['id']] = user_dict
        conn.close()
        return users
    except Exception as e:
        logging.error(f"Database Error: {e}")
        return {}

@beartype
def update_users(data: Dict[str, Dict[str, Union[str, List[str]]]]) -> None:
    pass

@cached(users_cache["_get_user_by_id"])
@beartype
def _get_user_by_id(user_id: str) -> Optional[Dict[str, Union[str, List[str], float]]]:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
        conn.close()
        
        if row:
            user_dict = {
                "id": row['id'],
                "nickname": row['nickname'],
                "password_hash": row['password_hash'],
                "time_registration": row['time_registration']
            }
            if row.get('email'):
                user_dict['email'] = row['email']
            if row.get('full_name'):
                user_dict['full_name'] = row['full_name']
            return user_dict
        return None
    except Exception as e:
        logging.error(f"Database Error: {e}")
        return None

@beartype
def get_user_by_id(
    user_id: str,
    keys: Optional[Iterable[str]] = None
) -> Optional[Dict[str, Union[str, List[str], float]]]:
    user = _get_user_by_id(user_id)
    
    if not user:
        return None
    
    if not keys:
        return user
    
    data = {}
    for key in keys:
        if key in user:
            data[key] = user[key]
    
    return data

@cached(users_cache["_get_user_by_nickname"])
@beartype
def _get_user_by_nickname(nickname: str) -> Optional[Dict[str, Union[str, List[str], float]]]:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE nickname = %s", (nickname,))
            row = cur.fetchone()
        conn.close()
        
        if row:
            user_dict = {
                "id": row['id'],
                "nickname": row['nickname'],
                "password_hash": row['password_hash'],
                "time_registration": row['time_registration']
            }
            if row.get('email'):
                user_dict['email'] = row['email']
            if row.get('full_name'):
                user_dict['full_name'] = row['full_name']
            return user_dict
        return None
    except Exception as e:
        logging.error(f"Database Error: {e}")
        return None

@beartype
def get_user_by_nickname(
    nickname: str,
    keys: Optional[Iterable[str]] = None
) -> Optional[Dict[str, Union[str, List[str], float]]]:
    user = _get_user_by_nickname(nickname)
    
    if not user:
        return None
    
    if not keys:
        return user
    
    data = {}
    for key in keys:
        if key in user:
            data[key] = user[key]
    
    return data

@beartype
def create_user(
    nickname: str,
    password_hash: str,
) -> str:
    user_id = _generate_user_id()
    time_reg = time.time()
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (id, nickname, password_hash, time_registration)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, nickname, password_hash, time_reg)
            )
        conn.close()
        clear_cache()
        return user_id
    except Exception as e:
        logging.error(f"Database Error: {e}")
        raise

@beartype
def delete_user(user_id: str):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.close()
        clear_cache()
    except Exception as e:
        logging.error(f"Database Error: {e}")
        raise

@beartype
def update_user(
    user_id: str,
    nickname: Optional[str] = None,
    password_hash: Optional[str] = None,
    email: Optional[str] = None,
    full_name: Optional[str] = None
) -> None:
    updates = []
    params = []
    
    if nickname is not None:
        updates.append("nickname = %s")
        params.append(nickname)
    if password_hash is not None:
        updates.append("password_hash = %s")
        params.append(password_hash)
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    if full_name is not None:
        updates.append("full_name = %s")
        params.append(full_name)
    
    if not updates:
        return
        
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
    params.append(user_id)
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
        conn.close()
        clear_cache()
    except Exception as e:
        logging.error(f"Database Error: {e}")
        raise