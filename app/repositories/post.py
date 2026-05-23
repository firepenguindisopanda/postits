from sqlmodel import Session, select
from app.models.post import Post
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

    def delete(self, post_id: int) -> None:
        post = self.db.get(Post, post_id)
        if post:
            self.db.delete(post)
            self.db.commit()
