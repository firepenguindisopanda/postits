from app.repositories.comment import CommentRepository


class CommentService:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    def create_comment(self, content: str, post_id: int, user_id: int):
        return self.comment_repo.create(content=content, post_id=post_id, user_id=user_id)

    def get_post_comments(self, post_id: int):
        return self.comment_repo.get_by_post(post_id)

    def delete_comment(self, comment_id: int):
        self.comment_repo.delete(comment_id)
