from sqlmodel import Session, select
from app.models.comment import Comment
from app.models.user import User
from typing import List


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, content: str, post_id: int, user_id: int) -> Comment:
        comment = Comment(content=content, post_id=post_id, user_id=user_id)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_post(self, post_id: int) -> List[Comment]:
        return self.db.exec(select(Comment).where(Comment.post_id == post_id)).all()

    def delete(self, comment_id: int) -> None:
        comment = self.db.get(Comment, comment_id)
        if comment:
            self.db.delete(comment)
            self.db.commit()
    
    def get_by_post_with_users(self, post_id: int) -> list[dict]:
        statement = (
            select(Comment, User.username)
            .join(User, Comment.user_id == User.user_id)
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        results = self.db.exec(statement).all()
        return [
            {
                "comment_id": c.comment_id,
                "content": c.content,
                "post_id": c.post_id,
                "user_id": c.user_id,
                "username": username,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c, username in results
        ]

    def get_all_comments_with_users(self) -> list[dict]:
        statement = (
            select(Comment, User.username)
            .join(User, Comment.user_id == User.user_id)
            .order_by(Comment.created_at.desc())
        )
        results = self.db.exec(statement).all()
        return [
            {
                "comment_id": c.comment_id,
                "content": c.content,
                "post_id": c.post_id,
                "user_id": c.user_id,
                "username": username,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c, username in results
        ]

    def get_all_comments(self) -> list:
        statement = (select(Comment.comment_id, Comment.content, Comment.post_id, Comment.created_at, Comment.user_id).order_by(Comment.created_at.desc()))
        return self.db.exec(statement).all()

