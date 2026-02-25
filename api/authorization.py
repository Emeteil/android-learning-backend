from fastapi import APIRouter, Request, Depends, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from utils.api_response import *
from utils.api_models import *
from api.schemas.authorization import *
from authorization import *
from utils.validation.user_data import (
    validate_register_data,
    NICKNAME_LENGTH,
    PASSWORD_LENGTH
)
from utils.password_hash import *
from utils.db.users import (
    get_user_by_nickname,
    create_user
)
from settings import app, limiter

router = APIRouter(prefix="/api/authorization", tags=["Authorization"])

@router.post(
    "/register", 
    response_model=ApiResponse[AuthResponse],
    status_code=201,
    summary="Register a new user",
    description="Creates a new user and sets an HTTP-only token cookie.",
    responses={
        201: {"model": ApiResponse[AuthResponse]},
        400: {"model": ApiErrorResponse}
    }
)
@limiter.limit("10 per 2 minute")
async def api_register(request: Request, response: Response, data: RegisterRequest):
    nickname: str = data.nickname
    password: str = data.password

    errors = validate_register_data(
        nickname,
        password
    )
    
    if len(errors) != 0:
        raise ApiError(400, errors)
    
    if get_user_by_nickname(nickname):
        raise ApiError(400, ["Nickname already exists"])

    password_hash = generate_password_hash(password)
    
    user_id: str = create_user(
        nickname,
        password_hash
    )
    
    token = generate_token(user_id, nickname)
    
    res = apiResponse({
        "message": "User registered successfully",
        "user_id": user_id,
        "nickname": nickname,
        "preferred_redirect": "/"
    }, 201)
    
    res.set_cookie("token", token, httponly=True, secure=True, samesite="Strict")
    
    return res

@router.post(
    "/login", 
    response_model=ApiResponse[AuthResponse],
    summary="User authorization",
    description="Verifies credentials and sets a token cookie.",
    responses={
        200: {"model": ApiResponse[AuthResponse]},
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse}
    }
)
@limiter.limit("6 per 3 minute")
async def api_login(request: Request, response: Response, data: LoginRequest):
    nickname = data.nickname[:NICKNAME_LENGTH[1]]
    password = data.password[:PASSWORD_LENGTH[1]]

    if not nickname or not password:
        raise ApiError(400, "Need “nickname” and “password” in data!")

    user = get_user_by_nickname(nickname)
    
    if not user or not check_password_hash(user["password_hash"], password):
        raise ApiError(401, "Invalid nickname or password!")
    
    token: str = generate_token(user["id"], user["nickname"])
    
    res = apiResponse({
        "message": "Login successful",
        "user_id": user["id"],
        "nickname": user["nickname"],
        "preferred_redirect": "/"
    }, 200)
    
    res.set_cookie("token", token)
    
    return res

@router.post(
    "/request_api_key", 
    response_model=ApiResponse[TokenResponse],
    status_code=201,
    summary="Request API key",
    description="Generates a new JWT token for an authorized user.",
    responses={
        201: {"model": ApiResponse[TokenResponse]},
        401: {"model": ApiErrorResponse}
    }
)
@limiter.limit("5 per 30 minute")
async def api_request_api_key(request: Request, payload: dict = Depends(login_required_headers)):
    token: str = generate_token(payload["user_id"], payload["nickname"])
    
    return apiResponse({
        "token": token
    }, 201)

app.include_router(router)