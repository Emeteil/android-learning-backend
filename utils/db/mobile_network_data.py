from typing import Dict, List, Optional, Any
from beartype import beartype
from settings import settings
import json
import os

MOBILE_DATA_DIR = settings["mobile_network_data"]["data_dir"]
FILE_EXTENSION = settings["mobile_network_data"]["file_extension"]

@beartype
def _get_user_file_path(user_id: str) -> str:
    os.makedirs(MOBILE_DATA_DIR, exist_ok=True)
    return os.path.join(MOBILE_DATA_DIR, f"{user_id}{FILE_EXTENSION}")

@beartype
def save_mobile_network_data(
    user_id: str,
    mobile_network_data_list: Optional[Dict[str, Any]] = None,
    location_data: Optional[Dict[str, Any]] = None
) -> bool:
    try:
        data = {
            "mobile_network_data_list": mobile_network_data_list or {},
            "location_data": location_data or {}
        }
        
        file_path = _get_user_file_path(user_id)
        
        with open(file_path, "a", encoding="utf-8") as f:
            json_str = json.dumps(data, ensure_ascii=False)
            f.write(json_str + "\n")
        
        return True
    except Exception:
        return False

@beartype
def get_user_mobile_data(
    user_id: str,
    page: int = 1,
    count: int = 100
) -> List[Dict[str, Any]]:
    try:
        file_path = _get_user_file_path(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[::-1]
        
        total_lines = len(lines)
        start_index = (page - 1) * count
        end_index = min(start_index + count, total_lines)
        
        if start_index >= total_lines or start_index < 0:
            return []
        
        data = []
        for line in lines[start_index:end_index]:
            try:
                data.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
        
        return data
    except Exception:
        return []

@beartype
def get_all_users_with_data() -> List[str]:
    try:
        if not os.path.exists(MOBILE_DATA_DIR):
            return []
        
        user_ids = []
        for filename in os.listdir(MOBILE_DATA_DIR):
            if filename.endswith(FILE_EXTENSION):
                user_id = filename[:-len(FILE_EXTENSION)]
                user_ids.append(user_id)
        
        return user_ids
    except Exception:
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
    except Exception:
        return {}

@beartype
def delete_user_mobile_data(user_id: str) -> bool:
    try:
        file_path = _get_user_file_path(user_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    except Exception:
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