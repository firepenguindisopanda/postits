from sqlmodel import Field, SQLModel
from typing import Optional
from pydantic import EmailStr
from datetime import datetime, timezone

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True, max_length=50)
    name: str = Field(max_length=100)
    email: EmailStr = Field(index=True, unique=True, max_length=255)
    role:str = Field(default="")

class User(UserBase, table=True):
    __tablename__: str = "users"
    user_id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
