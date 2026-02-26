from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from typing import Optional
import time
import json
from fastapi.concurrency import run_in_threadpool

from authorization import login_required_cookies, _verify_token
from utils.api_response import apiResponse, ApiError
from utils.api_models import ApiResponse, ApiErrorResponse
from utils.db.users import get_user_by_nickname, get_user_by_id
from utils.db.mobile_network_data import (
    save_mobile_network_data,
    get_user_mobile_data,
    get_user_mobile_data_by_nickname,
    get_all_mobile_data,
    get_all_users_with_data,
    delete_user_mobile_data
)
from utils.connection_manager import manager
from settings import app, settings
from api.schemas.mobile_network import (
    MobileDataSaveRequest,
    MobileDataResponseItem,
    UsersWithDataResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/mobile-network", tags=["Mobile Network Data"])

DEFAULT_PAGE = settings.get("mobile_network_data", {}).get("default_page", 1)
DEFAULT_COUNT = settings.get("mobile_network_data", {}).get("default_count", 100)
MAX_COUNT = settings.get("mobile_network_data", {}).get("max_count", 1000)

@router.post(
    "/data",
    summary="Save mobile network data",
    response_model=ApiResponse[SuccessResponse],
    responses={
        201: {"model": ApiResponse[SuccessResponse]},
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse}
    }
)
async def api_save_mobile_data(
    data: MobileDataSaveRequest,
    payload: dict = Depends(login_required_cookies)
):
    request_dump = data.model_dump(by_alias=True, exclude_none=True)
    mobile_network_data_list = request_dump.get("mobile_network_data_list")
    location_data = request_dump.get("location_data")
    
    user_id = payload.get("user_id")

    if not mobile_network_data_list and not location_data:
        raise ApiError(400)
    
    success = await run_in_threadpool(
        save_mobile_network_data,
        user_id,
        mobile_network_data_list,
        location_data
    )
    
    if not success:
        raise ApiError(500)
    
    return apiResponse({"message": "Data saved successfully"}, 201)

@router.get(
    "/data",
    summary="Get mobile network data",
    response_model=ApiResponse[MobileDataResponseItem]
)
async def api_get_mobile_data(
    page: int = DEFAULT_PAGE,
    count: int = DEFAULT_COUNT,
    user_id: Optional[str] = None,
    nickname: Optional[str] = None
):
    if page < 1:
        page = DEFAULT_PAGE
    if count < 1:
        count = DEFAULT_COUNT
    if count > MAX_COUNT:
        count = MAX_COUNT
    
    if user_id:
        data = await run_in_threadpool(get_user_mobile_data, user_id, page, count)
        return apiResponse({
            "user_id": user_id,
            "data": data,
            "page": page,
            "count": len(data)
        })
    elif nickname:
        data = await run_in_threadpool(get_user_mobile_data_by_nickname, nickname, page, count)
        user = await run_in_threadpool(get_user_by_nickname, nickname, ["id"])
        return apiResponse({
            "nickname": nickname,
            "user_id": user["id"] if user else None,
            "data": data,
            "page": page,
            "count": len(data)
        })
    else:
        data = await run_in_threadpool(get_all_mobile_data, page, count)
        return apiResponse({
            "data": data,
            "page": page,
            "count": len(data)
        })

@router.get(
    "/users",
    response_model=ApiResponse[UsersWithDataResponse],
    summary="Get users with mobile network data"
)
async def api_get_users_with_data():
    users = await run_in_threadpool(get_all_users_with_data)
    
    users_with_nicknames = []
    for user_id in users:
        user = await run_in_threadpool(get_user_by_id, user_id, ["nickname"])
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

@router.delete(
    "/data",
    summary="Delete mobile network data",
    response_model=ApiResponse[SuccessResponse],
    responses={
        200: {"model": ApiResponse[SuccessResponse]},
        401: {"model": ApiErrorResponse}
    }
)
async def api_delete_mobile_data(
    payload: dict = Depends(login_required_cookies)
):
    user_id = payload.get("user_id")
    success = await run_in_threadpool(delete_user_mobile_data, user_id)
    
    if not success:
        return apiResponse({"message": "No data to delete"}, 200)
    
    return apiResponse({"message": "Data deleted successfully"}, 200)

@router.delete(
    "/data/{user_id}",
    summary="Delete specific user mobile network data",
    response_model=ApiResponse[SuccessResponse],
    responses={
        200: {"model": ApiResponse[SuccessResponse]},
        401: {"model": ApiErrorResponse},
        403: {"model": ApiErrorResponse}
    }
)
async def api_delete_specific_user_mobile_data(
    user_id: str,
    payload: dict = Depends(login_required_cookies)
):
    current_user_id = payload.get("user_id")
    
    if current_user_id != user_id:
        raise ApiError(403)
    
    success = await run_in_threadpool(delete_user_mobile_data, user_id)
    
    if not success:
        return apiResponse({"message": "No data to delete"}, 200)
    
    return apiResponse({"message": "Data deleted successfully"}, 200)

@router.websocket("/ws")
async def mobile_network_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token") or websocket.cookies.get("token")
    is_authenticated = False
    user_id = None
    nickname = None
    
    if token:
        payload = _verify_token(token)
        if payload:
            user = await run_in_threadpool(get_user_by_id, payload.get("user_id"), ["nickname"])
            if user:
                is_authenticated = True
                user_id = payload.get("user_id")
                nickname = user.get("nickname")

    connection_id = f"{user_id or 'anonymous'}_{int(time.time()*1000)}"
    
    await manager.connect(websocket, connection_id)
    if not is_authenticated:
        await manager.join_room(connection_id, "anonymous_mobile_network")
        
    try:
        while True:
            raw_data = await websocket.receive_text()
            
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                continue
                
            if is_authenticated and user_id:
                try:
                    parsed_data = MobileDataSaveRequest(**data)
                except Exception as e:
                    await manager.send_personal_message(
                        {"status": "error", "message": "Invalid data format"},
                        connection_id
                    )
                    continue

                request_dump = parsed_data.model_dump(by_alias=True, exclude_none=True)
                mobile_network_data_list = request_dump.get("mobile_network_data_list")
                location_data = request_dump.get("location_data")
                
                if mobile_network_data_list or location_data:
                    await run_in_threadpool(
                        save_mobile_network_data,
                        user_id,
                        mobile_network_data_list,
                        location_data
                    )
                    
                    broadcast_data = {
                        nickname: {
                            "mobile_network_data_list": mobile_network_data_list,
                            "location_data": location_data
                        }
                    }
                    
                    await manager.send_to_room(
                        broadcast_data,
                        "anonymous_mobile_network"
                    )
                    
                    await manager.send_personal_message(
                        {"status": "success", "message": "Data saved"},
                        connection_id
                    )
            else:
                await manager.send_personal_message(
                    {"status": "error", "message": "Receive/Read mode only"},
                    connection_id
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, connection_id)

app.include_router(router)