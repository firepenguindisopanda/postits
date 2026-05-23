from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.comment import Comment

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True, max_length=50)
    name: str = Field(default="", max_length=100)
    email: EmailStr = Field(index=True, unique=True, max_length=255)
    role:str = Field(default="")

class User(UserBase, table=True):
    __tablename__: str = "users"
    user_id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    posts: List["Post"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")
