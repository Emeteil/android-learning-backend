from typing import Dict, List, Optional, Any
from beartype import beartype
import json

from utils.db.connection import get_db_connection

@beartype
def save_mobile_network_data(
    user_id: str,
    mobile_network_data_list: Optional[Dict[str, Any]] = None,
    location_data: Optional[Dict[str, Any]] = None
) -> bool:
    try:
        conn = get_db_connection()
        
        latitude = location_data.get('Latitude') if location_data else None
        longitude = location_data.get('Longitude') if location_data else None
        altitude = location_data.get('Altitude') if location_data else None
        loc_time = location_data.get('Time') if location_data else None
        
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mobile_data (
                    user_id, mobile_network_data_list, 
                    latitude, longitude, altitude, time
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    json.dumps(mobile_network_data_list) if mobile_network_data_list else None,
                    latitude,
                    longitude,
                    altitude,
                    loc_time
                )
            )
        conn.close()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

@beartype
def get_user_mobile_data(
    user_id: str,
    page: int = 1,
    count: int = 100
) -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            offset = (page - 1) * count
            cur.execute(
                """
                SELECT mobile_network_data_list, latitude, longitude, altitude, time 
                FROM mobile_data 
                WHERE user_id = %s 
                ORDER BY time DESC NULLS LAST 
                LIMIT %s OFFSET %s
                """,
                (user_id, count, offset)
            )
            rows = cur.fetchall()
            
            data = []
            for row in rows:
                loc_data = {}
                if row['latitude'] is not None:
                    loc_data['Latitude'] = row['latitude']
                if row['longitude'] is not None:
                    loc_data['Longitude'] = row['longitude']
                if row['altitude'] is not None:
                    loc_data['Altitude'] = row['altitude']
                if row['time'] is not None:
                    loc_data['Time'] = row['time']
                    
                item = {
                    "mobile_network_data_list": row['mobile_network_data_list'] or {},
                    "location_data": loc_data
                }
                data.append(item)
                
        conn.close()
        return data
    except Exception as e:
        print(f"Database Error: {e}")
        return []

@beartype
def get_all_users_with_data() -> List[str]:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM mobile_data")
            rows = cur.fetchall()
            user_ids = [row['user_id'] for row in rows]
        conn.close()
        return user_ids
    except Exception as e:
        print(f"Database Error: {e}")
        return []

@beartype
def get_all_mobile_data(
    page: int = 1,
    count: int = 100
) -> Dict[str, List[Dict[str, Any]]]:
    try:
        user_ids = get_all_users_with_data()
        if not user_ids:
            return {}
        
        all_data = {}
        total_users = len(user_ids)
        start_index = (page - 1) * count
        end_index = min(start_index + count, total_users)
        
        if start_index >= total_users or start_index < 0:
            return {}
        
        for user_id in user_ids[start_index:end_index]:
            user_data = get_user_mobile_data(user_id, page=1, count=10)
            if user_data:
                all_data[user_id] = user_data
        
        return all_data
    except Exception as e:
        print(f"Database Error: {e}")
        return {}

@beartype
def delete_user_mobile_data(user_id: str) -> bool:
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mobile_data WHERE user_id = %s", (user_id,))
            affected = cur.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Database Error: {e}")
        return False

@beartype
def get_user_mobile_data_by_nickname(
    nickname: str,
    page: int = 1,
    count: int = 100
) -> List[Dict[str, Any]]:
    from utils.db.users import get_user_by_nickname
    
    user = get_user_by_nickname(nickname, ["id"])
    if not user:
        return []
    
    return get_user_mobile_data(user["id"], page, count)