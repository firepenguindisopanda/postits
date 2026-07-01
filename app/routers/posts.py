from fastapi import status
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.post import PostRepository
from app.services.post_service import PostService
from . import api_router
from pydantic import BaseModel
from typing import Optional, List


class PostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = None


class PostResponse(BaseModel):
    post_id: int
    content: str
    media_urls: Optional[List[str]]
    user_id: int


class FeedPostResponse(BaseModel):
    post_id: int
    content: str
    media_urls: Optional[List[str]] = None
    user_id: int
    username: str = ""
    created_at: str = ""
    comment_count: int = 0


@api_router.get("/feed", response_model=list[FeedPostResponse])
async def feed_posts(db: SessionDep):
    repo = PostRepository(db)
    service = PostService(repo)
    return service.get_feed()


@api_router.get("/posts", response_model=list[PostResponse])
async def list_posts(db: SessionDep):
    repo = PostRepository(db)
    service = PostService(repo)
    return service.get_all_posts()


@api_router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, db: SessionDep, user: AuthDep):
    repo = PostRepository(db)
    service = PostService(repo)
    return service.create_post(content=post_data.content, user_id=user.user_id, media_urls=post_data.media_urls)


@api_router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: SessionDep):
    repo = PostRepository(db)
    service = PostService(repo)
    post = service.get_post(post_id)
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@api_router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: SessionDep, user: AuthDep):
    repo = PostRepository(db)
    service = PostService(repo)
    service.delete_post(post_id)
