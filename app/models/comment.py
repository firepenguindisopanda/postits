from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class CommentBase(SQLModel):
    content: str = Field(nullable=False)


class Comment(CommentBase, table=True):
    __tablename__ = "comments"

    comment_id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.post_id", nullable=False, index=True)
    user_id: int = Field(foreign_key="users.user_id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    post: Optional["Post"] = Relationship(back_populates="comments")
    user: Optional["User"] = Relationship(back_populates="comments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.content or not self.content.strip():
            raise ValueError("content must not be empty")
