from sqlmodel import Session, select, func
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from typing import Optional, List


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, content: str, user_id: int, media_urls: Optional[List[str]] = None) -> Post:
        post = Post(content=content, user_id=user_id, media_urls=media_urls)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.get(Post, post_id)

    def get_by_user(self, user_id: int) -> List[Post]:
        return self.db.exec(select(Post).where(Post.user_id == user_id)).all()

    def get_all(self) -> List[Post]:
        return self.db.exec(select(Post)).all()

    def get_all_with_users(self) -> list[dict]:
        statement = (
            select(Post, User.username)
            .join(User, Post.user_id == User.user_id)
            .order_by(Post.created_at.desc())
        )
        results = self.db.exec(statement).all()
        return [
            {
                "post_id": post.post_id,
                "content": post.content,
                "username": username,
                "user_id": post.user_id,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "media_urls": post.media_urls,
            }
            for post, username in results
        ]

    def get_comment_count(self, post_id: int) -> int:
        statement = select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        result = self.db.exec(statement).one()
        return result

    def delete(self, post_id: int) -> None:
        post = self.db.get(Post, post_id)
        if post:
            self.db.delete(post)
            self.db.commit()
