from pydantic import BaseModel, Field

class PingResponse(BaseModel):
    message: str = Field(..., description="Ping response message", example="Pong!")