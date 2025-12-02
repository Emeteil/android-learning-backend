from flask import request
from utils.db.users import get_user_by_nickname, get_user_by_id
from utils.api_response import apiResponse, ApiError
from authorization import login_required
from utils.db.mobile_network_data import *
from settings import *

DEFAULT_PAGE = settings["mobile_network_data"]["default_page"]
DEFAULT_COUNT = settings["mobile_network_data"]["default_count"]
MAX_COUNT = settings["mobile_network_data"]["max_count"]

@app.route("/api/mobile-network/data", methods=["POST"])
@login_required("cookies")
def api_save_mobile_data(payload):
    data = request.get_json()
    
    if not data:
        raise ApiError(400)
    
    mobile_network_data_list = data.get("mobile_network_data_list")
    location_data = data.get("location_data")
    
    if not mobile_network_data_list and not location_data:
        raise ApiError(400)
    
    user_id = payload.get("user_id")
    
    success = save_mobile_network_data(
        user_id,
        mobile_network_data_list,
        location_data
    )
    
    if not success:
        raise ApiError(500)
    
    return apiResponse({"message": "Data saved successfully"}, 201)

@app.route("/api/mobile-network/data", methods=["GET"])
def api_get_mobile_data():
    page = request.args.get("page", DEFAULT_PAGE, type=int)
    count = request.args.get("count", DEFAULT_COUNT, type=int)
    
    if page < 1:
        page = DEFAULT_PAGE
    if count < 1:
        count = DEFAULT_COUNT
    if count > MAX_COUNT:
        count = MAX_COUNT
    
    user_id = request.args.get("user_id")
    nickname = request.args.get("nickname")
    
    if user_id:
        data = get_user_mobile_data(user_id, page, count)
        return apiResponse({
            "user_id": user_id,
            "data": data,
            "page": page,
            "count": len(data)
        })
    
    elif nickname:
        data = get_user_mobile_data_by_nickname(nickname, page, count)
        user = get_user_by_nickname(nickname, ["id"])
        return apiResponse({
            "nickname": nickname,
            "user_id": user["id"] if user else None,
            "data": data,
            "page": page,
            "count": len(data)
        })
    
    else:
        data = get_all_mobile_data(page, count)
        return apiResponse({
            "data": data,
            "page": page,
            "count": len(data)
        })

@app.route("/api/mobile-network/users", methods=["GET"])
def api_get_users_with_data():
    users = get_all_users_with_data()
    
    users_with_nicknames = []
    for user_id in users:
        user = get_user_by_id(user_id, ["nickname"])
        if user:
            users_with_nicknames.append({
                "user_id": user_id,
                "nickname": user.get("nickname")
            })
        else:
            users_with_nicknames.append({
                "user_id": user_id,
                "nickname": None
            })
    
    return apiResponse({
        "users": users_with_nicknames,
        "total": len(users_with_nicknames)
    })

@app.route("/api/mobile-network/data", methods=["DELETE"])
@login_required("cookies")
def api_delete_mobile_data(payload):
    user_id = payload.get("user_id")
    
    success = delete_user_mobile_data(user_id)
    
    if not success:
        return apiResponse({"message": "No data to delete"}, 200)
    
    return apiResponse({"message": "Data deleted successfully"}, 200)

@app.route("/api/mobile-network/data/<user_id>", methods=["DELETE"])
@login_required("cookies")
def api_delete_specific_user_mobile_data(payload, user_id):
    current_user_id = payload.get("user_id")
    
    if current_user_id != user_id:
        # from utils.db.users import get_user_by_id
        # current_user = get_user_by_id(current_user_id, ["nickname"])
        # if not current_user or current_user.get("nickname") != "admin":
            raise ApiError(403)
    
    success = delete_user_mobile_data(user_id)
    
    if not success:
        return apiResponse({"message": "No data to delete"}, 200)
    
    return apiResponse({"message": "Data deleted successfully"}, 200)