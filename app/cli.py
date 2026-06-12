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


@comments_app.command("list-all")
def comment_list_all():
    with get_cli_session() as session:
        repo = CommentRepository(session)
        comments = repo.get_all_comments()
        rows = [[c.comment_id, c.content[:60], c.post_id, c.user_id, c.created_at] for c in comments]
        print_table(rows, headers=["ID", "Content", "Post ID", "User ID", "Created At"])


@comments_app.command("delete")
def comment_delete(comment_id: int = typer.Argument(..., help="Comment ID")):
    with get_cli_session() as session:
        repo = CommentRepository(session)
        repo.delete(comment_id)
        typer.echo(f"Comment {comment_id} deleted")


@app.command("seed")
def seed(
    force: bool = typer.Option(False, "--force", "-f", help="Drop existing data before seeding"),
):
    if force:
        from app.database import drop_all, create_db_and_tables
        drop_all()
        create_db_and_tables()
        typer.echo("Dropped existing tables and recreated them.")
    with get_cli_session() as session:
        user_repo = UserRepository(session)
        post_repo = PostRepository(session)
        comment_repo = CommentRepository(session)

        users_data = [
            ("alice", "alice@example.com", encrypt_password("password"), "Alice Johnson", "admin"),
            ("bob", "bob@example.com", encrypt_password("password"), "Bob Smith", "regular_user"),
            ("charlie", "charlie@example.com", encrypt_password("password"), "Charlie Brown", "regular_user"),
            ("diana", "diana@example.com", encrypt_password("password"), "Diana Prince", "regular_user"),
            ("eve", "eve@example.com", encrypt_password("password"), "Eve Adams", "regular_user"),
        ]
        users = []
        for username, email, pwd, name, role in users_data:
            user = User(username=username, email=email, password=pwd, name=name, role=role)
            users.append(user_repo.create(user))
        typer.echo(f"Created {len(users)} users")

        posts_data = [
            ("Just finished reading a great book on machine learning. Highly recommend 'Deep Learning with Python'!", users[0].user_id, None),
            ("Beautiful sunset at the beach today! 🏖️", users[1].user_id, ["https://example.com/sunset.jpg"]),
            ("Anyone else excited about the new Python 3.14 features?", users[2].user_id, None),
            ("Looking for recommendations on good VS Code extensions for web development.", users[3].user_id, None),
            ("Deployed my first FastAPI app to production! 🚀", users[0].user_id, None),
            ("Morning coffee and coding. The perfect combination.", users[4].user_id, None),
            ("Tips for staying focused during long coding sessions?", users[1].user_id, None),
            ("Finally understood how async/await works in Python. Game changer!", users[2].user_id, ["https://example.com/async.jpg"]),
        ]
        posts = []
        for content, user_id, media_urls in posts_data:
            posts.append(post_repo.create(content=content, user_id=user_id, media_urls=media_urls))
        typer.echo(f"Created {len(posts)} posts")

        comments_data = [
            ("Thanks for the recommendation! Adding it to my reading list.", posts[0].post_id, users[1].user_id),
            ("I've read that too, it's fantastic!", posts[0].post_id, users[2].user_id),
            ("Great shot! Where was this taken?", posts[1].post_id, users[0].user_id),
            ("The match statement is going to be amazing.", posts[2].post_id, users[3].user_id),
            ("I use Prettier and ESLint — they're must-haves.", posts[3].post_id, users[4].user_id),
            ("Congrats! What hosting provider did you go with?", posts[4].post_id, users[1].user_id),
            ("Nothing beats a good cup of coffee while coding.", posts[5].post_id, users[0].user_id),
            ("I use the Pomodoro technique — 25 min work, 5 min break.", posts[6].post_id, users[2].user_id),
            ("Same here! It clicked after watching a talk by Łukasz Langa.", posts[7].post_id, users[3].user_id),
            ("The structural pattern matching is a lifesaver for parsing.", posts[7].post_id, users[4].user_id),
            ("What book are you reading next?", posts[0].post_id, users[3].user_id),
            ("Try the GitHub Copilot extension, it's a game changer!", posts[3].post_id, users[0].user_id),
            ("How was the deployment process? Any issues?", posts[4].post_id, users[2].user_id),
            ("I prefer noise-cancelling headphones and lo-fi music.", posts[6].post_id, users[4].user_id),
            ("Can you share the async code pattern you used?", posts[7].post_id, users[1].user_id),
        ]
        for content, post_id, user_id in comments_data:
            comment_repo.create(content=content, post_id=post_id, user_id=user_id)
        typer.echo(f"Created {len(comments_data)} comments")

        typer.echo("Database seeded successfully!")


if __name__ == "__main__":
    app()
