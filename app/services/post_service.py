from app.repositories.post import PostRepository
from typing import Optional, List


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def create_post(self, content: str, user_id: int, media_urls: Optional[List[str]] = None):
        return self.post_repo.create(content=content, user_id=user_id, media_urls=media_urls)

    def get_post(self, post_id: int):
        return self.post_repo.get_by_id(post_id)

    def get_user_posts(self, user_id: int):
        return self.post_repo.get_by_user(user_id)

    def get_all_posts(self):
        return self.post_repo.get_all()

    def get_feed(self):
        posts = self.post_repo.get_all_with_users()
        for post in posts:
            post["comment_count"] = self.post_repo.get_comment_count(post["post_id"])
        return posts

    def delete_post(self, post_id: int):
        self.post_repo.delete(post_id)
