from fastapi import APIRouter, Depends, Request
from authorization import login_required_cookies
from utils.api_response import *
from utils.api_models import ApiResponse, ApiErrorResponse
from api.schemas.admin import PingResponse
from settings import app

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get(
    "/ping", 
    response_model=ApiResponse[PingResponse],
    summary="Check server availability",
    description="Returns 'Pong!' if the server is running.",
    responses={200: {"model": ApiResponse[PingResponse]}}
)
async def ping_server():
    return apiResponse({"message": "Pong!"})

@router.get(
    "/loged_ping", 
    response_model=ApiResponse[PingResponse],
    summary="Check availability with authorization",
    description="Returns 'Pong!' if the user is authorized via cookies.",
    responses={
        200: {"model": ApiResponse[PingResponse]},
        401: {"model": ApiErrorResponse}
    }
)
async def loged_ping_server(payload: dict = Depends(login_required_cookies)):
    return apiResponse({"message": "Pong!"})

@app.get("/error_page", include_in_schema=False)
async def error_page_cheack(request: Request):
    status_code: int = int(request.query_params.get("code", 500))
    raise ApiError(
        code = status_code
    )

app.include_router(router)