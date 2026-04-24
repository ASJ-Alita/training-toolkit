"""
认证相关 Pydantic Schema
"""

from pydantic import BaseModel, Field


# ---------- 请求 ----------

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=4, max_length=128)
    display_name: str = Field(default="", max_length=50)
    role: str = Field(default="student", pattern=r"^(admin|student)$")
    student_id: str = Field(default="", max_length=8)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4, max_length=128)


# ---------- 响应 ----------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    username: str
    display_name: str
    role: str
    student_id: str

    model_config = {"from_attributes": True}


# 需要放在类定义后，Pydantic v2 支持 forward ref
TokenResponse.model_rebuild()
