from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.comment import Comment


class PostBase(SQLModel):
    content: str = Field(nullable=False)
    media_urls: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )


class Post(PostBase, table=True):
    __tablename__ = "posts"

    post_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    user: Optional["User"] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.content or not self.content.strip():
            raise ValueError("content must not be empty")
