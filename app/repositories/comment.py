from sqlmodel import Session, select
from app.models.comment import Comment
from typing import List, Tuple, Any


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
    
    def get_all_comments(self) -> List[Tuple[int, str,Any]]:
        statement = (select(Comment.comment_id, Comment.content, Comment.created_at, Comment.user_id).order_by(Comment.created_at.desc()))
        return self.db.exec(statement).all()

