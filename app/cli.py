import typer
from typing import Optional
from tabulate import tabulate
from app.database import get_cli_session
from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.repositories.comment import CommentRepository
from app.utilities.security import encrypt_password
from app.models.user import User
from app.schemas.user import UserUpdate

app = typer.Typer()
users_app = typer.Typer()
posts_app = typer.Typer()
comments_app = typer.Typer()
app.add_typer(users_app, name="users", help="Manage users")
app.add_typer(posts_app, name="posts", help="Manage posts")
app.add_typer(comments_app, name="comments", help="Manage comments")


def print_table(rows, headers):
    print(tabulate(rows, headers=headers, tablefmt="grid"))



@users_app.command("create")
def user_create(
    username: str = typer.Argument(..., help="Username"),
    email: str = typer.Argument(..., help="Email address"),
    password: str = typer.Argument(..., help="Password"),
    name: Optional[str] = typer.Option(None, help="Display name"),
    role: str = typer.Option("regular_user", help="Role (admin, regular_user)"),
):
    with get_cli_session() as session:
        repo = UserRepository(session)
        user = User(
            username=username,
            email=email,
            password=encrypt_password(password),
            name=name or username,
            role=role,
        )
        created = repo.create(user)
        print_table(
            [[created.user_id, created.username, created.email, created.name, created.role]],
            headers=["ID", "Username", "Email", "Name", "Role"],
        )


@users_app.command("list")
def user_list():
    with get_cli_session() as session:
        repo = UserRepository(session)
        users = repo.get_all_users()
        rows = [[u.user_id, u.username, u.email, u.name, u.role] for u in users]
        print_table(rows, headers=["ID", "Username", "Email", "Name", "Role"])


@users_app.command("get")
def user_get(user_id: int = typer.Argument(..., help="User ID")):
    with get_cli_session() as session:
        repo = UserRepository(session)
        user = repo.get_by_id(user_id)
        if not user:
            typer.echo(f"User {user_id} not found", err=True)
            raise typer.Exit(1)
        print_table(
            [[user.user_id, user.username, user.email, user.name, user.role]],
            headers=["ID", "Username", "Email", "Name", "Role"],
        )


@users_app.command("update")
def user_update(
    user_id: int = typer.Argument(..., help="User ID"),
    username: Optional[str] = typer.Option(None, help="New username"),
    email: Optional[str] = typer.Option(None, help="New email"),
):
    with get_cli_session() as session:
        repo = UserRepository(session)
        data = UserUpdate(username=username, email=email)
        updated = repo.update_user(user_id, data)
        print_table(
            [[updated.user_id, updated.username, updated.email, updated.name, updated.role]],
            headers=["ID", "Username", "Email", "Name", "Role"],
        )


@users_app.command("delete")
def user_delete(user_id: int = typer.Argument(..., help="User ID")):
    with get_cli_session() as session:
        repo = UserRepository(session)
        repo.delete_user(user_id)
        typer.echo(f"User {user_id} deleted")


@users_app.command("posts")
def user_posts(user_id: int = typer.Argument(..., help="User ID")):
    with get_cli_session() as session:
        post_repo = PostRepository(session)
        user_repo = UserRepository(session)
        user = user_repo.get_by_id(user_id)
        if not user:
            typer.echo(f"User {user_id} not found", err=True)
            raise typer.Exit(1)
        posts = post_repo.get_by_user(user_id)
        rows = [[p.post_id, p.content[:60], p.user_id, p.created_at] for p in posts]
        print_table(rows, headers=["ID", "Content", "User ID", "Created At"])



@posts_app.command("create")
def post_create(
    content: str = typer.Argument(..., help="Post content"),
    user_id: int = typer.Argument(..., help="Author user ID"),
    media_urls: Optional[str] = typer.Option(None, help="Comma-separated media URLs"),
):
    with get_cli_session() as session:
        repo = PostRepository(session)
        urls = [u.strip() for u in media_urls.split(",")] if media_urls else None
        post = repo.create(content=content, user_id=user_id, media_urls=urls)
        print_table(
            [[post.post_id, post.content[:60], post.user_id, post.created_at]],
            headers=["ID", "Content", "User ID", "Created At"],
        )


@posts_app.command("list")
def post_list():
    with get_cli_session() as session:
        repo = PostRepository(session)
        posts = repo.get_all()
        rows = [[p.post_id, p.content[:60], p.user_id, p.created_at] for p in posts]
        print_table(rows, headers=["ID", "Content", "User ID", "Created At"])


@posts_app.command("get")
def post_get(post_id: int = typer.Argument(..., help="Post ID")):
    with get_cli_session() as session:
        repo = PostRepository(session)
        post = repo.get_by_id(post_id)
        if not post:
            typer.echo(f"Post {post_id} not found", err=True)
            raise typer.Exit(1)
        print_table(
            [[post.post_id, post.content, post.user_id, post.created_at]],
            headers=["ID", "Content", "User ID", "Created At"],
        )


@posts_app.command("delete")
def post_delete(post_id: int = typer.Argument(..., help="Post ID")):
    with get_cli_session() as session:
        repo = PostRepository(session)
        repo.delete(post_id)
        typer.echo(f"Post {post_id} deleted")


@posts_app.command("comments")
def post_comments(post_id: int = typer.Argument(..., help="Post ID")):
    with get_cli_session() as session:
        comment_repo = CommentRepository(session)
        post_repo = PostRepository(session)
        post = post_repo.get_by_id(post_id)
        if not post:
            typer.echo(f"Post {post_id} not found", err=True)
            raise typer.Exit(1)
        comments = comment_repo.get_by_post(post_id)
        rows = [[c.comment_id, c.content[:60], c.post_id, c.user_id, c.created_at] for c in comments]
        print_table(rows, headers=["ID", "Content", "Post ID", "User ID", "Created At"])



@comments_app.command("create")
def comment_create(
    content: str = typer.Argument(..., help="Comment content"),
    post_id: int = typer.Argument(..., help="Post ID"),
    user_id: int = typer.Argument(..., help="Author user ID"),
):
    with get_cli_session() as session:
        repo = CommentRepository(session)
        comment = repo.create(content=content, post_id=post_id, user_id=user_id)
        print_table(
            [[comment.comment_id, comment.content[:60], comment.post_id, comment.user_id, comment.created_at]],
            headers=["ID", "Content", "Post ID", "User ID", "Created At"],
        )


@comments_app.command("list")
def comment_list(post_id: int = typer.Argument(..., help="Post ID to list comments for")):
    with get_cli_session() as session:
        repo = CommentRepository(session)
        comments = repo.get_by_post(post_id)
        rows = [[c.comment_id, c.content[:60], c.post_id, c.user_id, c.created_at] for c in comments]
        print_table(rows, headers=["ID", "Content", "Post ID", "User ID", "Created At"])


@comments_app.command("delete")
def comment_delete(comment_id: int = typer.Argument(..., help="Comment ID")):
    with get_cli_session() as session:
        repo = CommentRepository(session)
        repo.delete(comment_id)
        typer.echo(f"Comment {comment_id} deleted")


if __name__ == "__main__":
    app()
