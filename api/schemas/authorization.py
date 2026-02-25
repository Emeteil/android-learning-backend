from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    nickname: str = Field(..., description="User nickname", example="user123")
    password: str = Field(..., description="User password", example="strongpassword")

class RegisterRequest(LoginRequest):
    pass

class AuthResponse(BaseModel):
    message: str = Field(..., description="Success message", example="Login successful")
    user_id: str = Field(..., description="User unique ID", example="user_123")
    nickname: str = Field(..., description="User nickname", example="user123")
    preferred_redirect: str = Field("/", description="Recommended redirect path")

class TokenResponse(BaseModel):
    token: str = Field(..., description="JWT access token")
