import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate
from app.schemas.auth import SignupRequest
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
def repo(db):
    return UserRepository(db)


@pytest.fixture
def sample_user(db):
    user = User(
        username="samples",
        name="Sample User",
        email="sample@example.com",
        password=encrypt_password("Pass123!"),
        role="regular_user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestUserRepository:
    def test_create_user(self, repo, db):
        user_data = SignupRequest(
            username="newuser",
            email="new@example.com",
            password=encrypt_password("NewPass123!"),
        )
        db_user = User.model_validate(user_data)
        result = repo.create(db_user)
        assert result.user_id is not None
        assert result.username == "newuser"
        assert result.email == "new@example.com"

    def test_create_user_duplicate_username(self, repo, sample_user):
        user_data = SignupRequest(
            username=sample_user.username,
            email="other@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_user = User.model_validate(user_data)
        with pytest.raises(Exception):
            repo.create(db_user)

    def test_get_by_username_found(self, repo, sample_user):
        result = repo.get_by_username("samples")
        assert result is not None
        assert result.email == "sample@example.com"

    def test_get_by_username_not_found(self, repo):
        result = repo.get_by_username("nonexistent")
        assert result is None

    def test_get_by_username_empty_string(self, repo):
        result = repo.get_by_username("")
        assert result is None

    def test_get_by_id_found(self, repo, sample_user):
        result = repo.get_by_id(sample_user.user_id)
        assert result is not None
        assert result.username == "samples"

    def test_get_by_id_not_found(self, repo):
        result = repo.get_by_id(99999)
        assert result is None

    def test_get_all_users_empty(self, repo):
        users = repo.get_all_users()
        assert users == []

    def test_get_all_users_multiple(self, repo, db):
        user1 = User(
            username="user_a",
            name="User A",
            email="a@example.com",
            password=encrypt_password("Pass123!"),
        )
        user2 = User(
            username="user_b",
            name="User B",
            email="b@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        users = repo.get_all_users()
        assert len(users) == 2

    def test_search_users_by_username(self, repo, sample_user):
        results, pagination = repo.search_users("samp")
        assert len(results) == 1
        assert results[0].username == "samples"

    def test_search_users_by_email(self, repo, sample_user):
        results, pagination = repo.search_users("sample@")
        assert len(results) >= 1

    def test_search_users_no_results(self, repo):
        results, pagination = repo.search_users("zzzzz")
        assert len(results) == 0

    def test_search_users_empty_query(self, repo, sample_user):
        results, pagination = repo.search_users("")
        assert len(results) >= 1

    def test_update_user_username(self, repo, sample_user):
        updated = repo.update_user(
            sample_user.user_id,
            UserUpdate(username="updatedname", email=None),
        )
        assert updated.username == "updatedname"
        assert updated.email == sample_user.email

    def test_update_user_email(self, repo, sample_user):
        updated = repo.update_user(
            sample_user.user_id,
            UserUpdate(username=None, email="updated@example.com"),
        )
        assert updated.email == "updated@example.com"
        assert updated.username == sample_user.username

    def test_update_user_invalid_id(self, repo):
        with pytest.raises(Exception, match="Invalid user id given"):
            repo.update_user(99999, UserUpdate(username="newname", email=None))

    def test_delete_user(self, repo, sample_user):
        repo.delete_user(sample_user.user_id)
        result = repo.get_by_id(sample_user.user_id)
        assert result is None

    def test_delete_user_invalid_id(self, repo):
        with pytest.raises(Exception, match="User doesn't exist"):
            repo.delete_user(99999)

    def test_search_users_pagination(self, repo, db):
        for i in range(15):
            user = User(
                username=f"paginate_user_{i}",
                name=f"User {i}",
                email=f"user{i}@example.com",
                password=encrypt_password("Pass123!"),
            )
            db.add(user)
        db.commit()
        results, pagination = repo.search_users("paginate_user_", page=1, limit=10)
        assert len(results) == 10
        assert pagination.total_pages == 2
        assert pagination.has_next
        assert not pagination.has_prev


class TestPostRepository:
    def test_create_post(self, db):
        from app.models.user import User
        from app.repositories.post import PostRepository
        user = User(
            username="postrepo_user",
            name="Post Repo",
            email="postrepo@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        post = repo.create(content="Test post", user_id=user.user_id)
        assert post.post_id is not None
        assert post.content == "Test post"
        assert post.user_id == user.user_id

    def test_get_post_by_id(self, db):
        from app.models.user import User
        from app.repositories.post import PostRepository
        user = User(
            username="postrepo2",
            name="Post Repo 2",
            email="postrepo2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        post = repo.create(content="Find me", user_id=user.user_id)
        found = repo.get_by_id(post.post_id)
        assert found is not None
        assert found.content == "Find me"

    def test_get_post_by_id_not_found(self, db):
        from app.repositories.post import PostRepository
        repo = PostRepository(db)
        result = repo.get_by_id(99999)
        assert result is None

    def test_get_posts_by_user(self, db):
        from app.models.user import User
        from app.repositories.post import PostRepository
        user = User(
            username="postrepo3",
            name="Post Repo 3",
            email="postrepo3@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        repo.create(content="Post A", user_id=user.user_id)
        repo.create(content="Post B", user_id=user.user_id)
        posts = repo.get_by_user(user.user_id)
        assert len(posts) == 2

    def test_delete_post(self, db):
        from app.models.user import User
        from app.repositories.post import PostRepository
        user = User(
            username="postrepo4",
            name="Post Repo 4",
            email="postrepo4@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        post = repo.create(content="Delete me", user_id=user.user_id)
        repo.delete(post.post_id)
        result = repo.get_by_id(post.post_id)
        assert result is None

    def test_get_all_posts(self, db):
        from app.models.user import User
        from app.repositories.post import PostRepository
        user = User(
            username="postrepo5",
            name="Post Repo 5",
            email="postrepo5@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        repo = PostRepository(db)
        repo.create(content="Post X", user_id=user.user_id)
        repo.create(content="Post Y", user_id=user.user_id)
        all_posts = repo.get_all()
        assert len(all_posts) == 2


class TestCommentRepository:
    def test_create_comment(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.repositories.comment import CommentRepository
        user = User(
            username="comrepo1",
            name="Com Repo 1",
            email="comrepo1@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        post = Post(content="Post for comment", user_id=user.user_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        repo = CommentRepository(db)
        comment = repo.create(content="Great post!", post_id=post.post_id, user_id=user.user_id)
        assert comment.comment_id is not None
        assert comment.content == "Great post!"

    def test_get_comments_by_post(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.repositories.comment import CommentRepository
        user = User(
            username="comrepo2",
            name="Com Repo 2",
            email="comrepo2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        post = Post(content="Post with comments", user_id=user.user_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        repo = CommentRepository(db)
        repo.create(content="C1", post_id=post.post_id, user_id=user.user_id)
        repo.create(content="C2", post_id=post.post_id, user_id=user.user_id)
        comments = repo.get_by_post(post.post_id)
        assert len(comments) == 2

    def test_delete_comment(self, db):
        from app.models.user import User
        from app.models.post import Post
        from app.repositories.comment import CommentRepository
        user = User(
            username="comrepo3",
            name="Com Repo 3",
            email="comrepo3@example.com",
            password=encrypt_password("Pass123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        post = Post(content="Post", user_id=user.user_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        repo = CommentRepository(db)
        comment = repo.create(content="Delete me", post_id=post.post_id, user_id=user.user_id)
        repo.delete(comment.comment_id)
        comments = repo.get_by_post(post.post_id)
        assert len(comments) == 0
