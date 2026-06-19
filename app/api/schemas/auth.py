from app.api.schemas.base import BaseSchema
from pydantic import Field, field_validator

class User(BaseSchema):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы и цифры')
        return v

class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"