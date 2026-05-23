from fastapi import status
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.comment import CommentRepository
from app.services.comment_service import CommentService
from . import api_router
from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str
    post_id: int


class CommentResponse(BaseModel):
    comment_id: int
    content: str
    post_id: int
    user_id: int


@api_router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(post_id: int, db: SessionDep):
    repo = CommentRepository(db)
    service = CommentService(repo)
    return service.get_post_comments(post_id)


@api_router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment_data: CommentCreate, db: SessionDep, user: AuthDep):
    repo = CommentRepository(db)
    service = CommentService(repo)
    return service.create_comment(content=comment_data.content, post_id=comment_data.post_id, user_id=user.user_id)


@api_router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: SessionDep, user: AuthDep):
    repo = CommentRepository(db)
    service = CommentService(repo)
    service.delete_comment(comment_id)
