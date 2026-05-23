import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utilities.security import encrypt_password


@pytest.fixture
def clean_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db(clean_engine):
    with Session(clean_engine) as session:
        yield session


@pytest.fixture
def user_repo(db):
    return UserRepository(db)


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)


@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)


@pytest.fixture
def existing_user(db):
    user = User(
        username="existing",
        name="Existing User",
        email="existing@example.com",
        password=encrypt_password("CorrectPass123!"),
        role="regular_user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestAuthService:
    def test_register_user_success(self, auth_service, db):
        user = auth_service.register_user("newguy", "newguy@example.com", "NewPass123!")
        assert user.username == "newguy"
        assert user.email == "newguy@example.com"
        assert user.role == "regular_user"

    def test_register_user_duplicate_username(self, auth_service, existing_user):
        with pytest.raises(Exception):
            auth_service.register_user(
                existing_user.username, "other@example.com", "Pass123!"
            )

    def test_register_user_duplicate_email(self, auth_service, existing_user):
        with pytest.raises(Exception):
            auth_service.register_user(
                "otheruser", existing_user.email, "Pass123!"
            )

    def test_authenticate_user_valid(self, auth_service, existing_user):
        token = auth_service.authenticate_user("existing", "CorrectPass123!")
        assert token is not None
        assert isinstance(token, str)

    def test_authenticate_user_wrong_password(self, auth_service, existing_user):
        token = auth_service.authenticate_user("existing", "WrongPassword!")
        assert token is None

    def test_authenticate_user_nonexistent(self, auth_service):
        token = auth_service.authenticate_user("nobody", "SomePass123!")
        assert token is None

    def test_register_user_password_encrypted(self, auth_service, db):
        user = auth_service.register_user("secrets", "secrets@example.com", "MyPassword!")
        assert user.password != "MyPassword!"
        assert user.password.startswith("$argon2id$")

    def test_register_empty_username(self, auth_service):
        with pytest.raises(Exception):
            auth_service.register_user("", "empty@example.com", "Pass123!")

    def test_register_invalid_email(self, auth_service):
        with pytest.raises(Exception):
            auth_service.register_user("bad_email", "not-an-email", "Pass123!")


class TestUserService:
    def test_get_all_users_empty(self, user_service):
        users = user_service.get_all_users()
        assert users == []

    def test_get_all_users_with_data(self, user_service, db):
        user1 = User(
            username="svc_user_a",
            name="Svc A",
            email="svca@example.com",
            password=encrypt_password("Pass123!"),
        )
        user2 = User(
            username="svc_user_b",
            name="Svc B",
            email="svcb@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        users = user_service.get_all_users()
        assert len(users) == 2


class TestPostService:
    def test_create_post(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.repositories.post import PostRepository
        from app.services.post_service import PostService
        user = User(
            username="postsvc",
            name="Post Svc",
            email="postsvc@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        service = PostService(repo)
        post = service.create_post(content="Service test", user_id=user.user_id)
        assert post.post_id is not None
        assert post.content == "Service test"

    def test_get_user_posts(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.repositories.post import PostRepository
        from app.services.post_service import PostService
        user = User(
            username="postsvc2",
            name="Post Svc 2",
            email="postsvc2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        service = PostService(repo)
        service.create_post(content="Post 1", user_id=user.user_id)
        service.create_post(content="Post 2", user_id=user.user_id)
        posts = service.get_user_posts(user.user_id)
        assert len(posts) == 2


class TestCommentService:
    def test_create_comment(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        from app.repositories.comment import CommentRepository
        from app.services.comment_service import CommentService
        user = User(
            username="comsvc",
            name="Com Svc",
            email="comsvc@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        post = Post(content="Svc post", user_id=user.user_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        repo = CommentRepository(db)
        service = CommentService(repo)
        comment = service.create_comment(content="Svc comment", post_id=post.post_id, user_id=user.user_id)
        assert comment.comment_id is not None
        assert comment.content == "Svc comment"

    def test_get_post_comments(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        from app.repositories.comment import CommentRepository
        from app.services.comment_service import CommentService
        user = User(
            username="comsvc2",
            name="Com Svc 2",
            email="comsvc2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        post = Post(content="Svc post 2", user_id=user.user_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        repo = CommentRepository(db)
        service = CommentService(repo)
        service.create_comment(content="C1", post_id=post.post_id, user_id=user.user_id)
        service.create_comment(content="C2", post_id=post.post_id, user_id=user.user_id)
        comments = service.get_post_comments(post.post_id)
        assert len(comments) == 2
