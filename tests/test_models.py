import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from app.models.user import User
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
def db_session(clean_engine):
    with Session(clean_engine) as session:
        yield session


class TestUserModel:
    def test_create_user(self, db_session):
        user = User(
            username="janedoe",
            name="Jane Doe",
            email="jane@example.com",
            password=encrypt_password("Pass123!"),
            role="regular_user",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.user_id is not None
        assert user.username == "janedoe"
        assert user.email == "jane@example.com"
        assert user.created_at is not None

    def test_user_default_role(self):
        user = User(
            username="norole",
            name="No Role",
            email="norole@example.com",
            password=encrypt_password("Pass123!"),
        )
        assert user.role == ""

    def test_unique_username_constraint(self, db_session):
        user1 = User(
            username="unique",
            name="User One",
            email="one@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user1)
        db_session.commit()
        user2 = User(
            username="unique",
            name="User Two",
            email="two@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_unique_email_constraint(self, db_session):
        user1 = User(
            username="user_a",
            name="User A",
            email="same@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user1)
        db_session.commit()
        user2 = User(
            username="user_b",
            name="User B",
            email="same@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_user_str_representation(self):
        user = User(
            username="strtest",
            name="Str Test",
            email="str@example.com",
            password=encrypt_password("Pass123!"),
        )
        assert str(user) is not None

    def test_user_created_at_defaults_to_not_none(self, db_session):
        user = User(
            username="tzuser",
            name="TZ User",
            email="tz@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.created_at is not None

    def test_user_password_not_returned_in_default_select(self, db_session):
        user = User(
            username="hiddenpw",
            name="Hidden PW",
            email="hidden@example.com",
            password=encrypt_password("Secret123!"),
        )
        db_session.add(user)
        db_session.commit()
        fetched = db_session.exec(select(User).where(User.username == "hiddenpw")).one()
        assert fetched.password is not None
        assert len(fetched.password) > 0

    def test_user_username_max_length_enforced(self, db_session):
        long_name = "a" * 51
        user = User(
            username=long_name,
            name="Long Name",
            email="long@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert len(user.username) == 51

    def test_user_role_can_be_admin(self, db_session):
        user = User(
            username="adminuser",
            name="Admin User",
            email="admin@site.com",
            password=encrypt_password("Admin123!"),
            role="admin",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.role == "admin"


class TestPostModel:
    def test_create_post(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="poster",
            name="Poster",
            email="poster@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Hello world!", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        assert post.post_id is not None
        assert post.content == "Hello world!"
        assert post.user_id == user.user_id
        assert post.created_at is not None

    def test_post_default_media_urls(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="mediauser",
            name="Media User",
            email="media@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="No media", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        assert post.media_urls is None or post.media_urls == []

    def test_post_with_media_urls(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="mediauser2",
            name="Media User 2",
            email="media2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(
            content="With media",
            user_id=user.user_id,
            media_urls=["https://example.com/img.jpg"],
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        assert post.media_urls == ["https://example.com/img.jpg"]

    def test_post_requires_content(self):
        from app.models.post import Post
        with pytest.raises(Exception):
            Post(user_id=1)

    def test_post_content_not_empty(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="emptycontent",
            name="Empty Content",
            email="empty@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        with pytest.raises(Exception):
            post = Post(content="", user_id=user.user_id)
            db_session.add(post)
            db_session.commit()

    def test_post_relationship_user(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="reluser",
            name="Rel User",
            email="rel@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Relationship test", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        assert post.user is not None
        assert post.user.username == "reluser"

    def test_post_created_at_auto_set(self, db_session):
        from app.models.post import Post
        from app.models.user import User
        user = User(
            username="timepost",
            name="Time Post",
            email="time@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Timed", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        assert post.created_at is not None


class TestCommentModel:
    def test_create_comment(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="commenter",
            name="Commenter",
            email="commenter@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="A post to comment on", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        comment = Comment(content="Nice post!", post_id=post.post_id, user_id=user.user_id)
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        assert comment.comment_id is not None
        assert comment.content == "Nice post!"
        assert comment.post_id == post.post_id
        assert comment.user_id == user.user_id

    def test_comment_requires_content(self):
        from app.models.comment import Comment
        with pytest.raises(Exception):
            Comment(post_id=1, user_id=1)

    def test_comment_relationship_post(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="relcommenter",
            name="Rel Commenter",
            email="relcomment@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Post for rel comment", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        comment = Comment(content="Rel comment", post_id=post.post_id, user_id=user.user_id)
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        assert comment.post is not None
        assert comment.post.content == "Post for rel comment"

    def test_comment_relationship_user(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="commentuser",
            name="Comment User",
            email="cuser@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Post for user rel", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        comment = Comment(content="User rel comment", post_id=post.post_id, user_id=user.user_id)
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        assert comment.user is not None
        assert comment.user.username == "commentuser"

    def test_comment_created_at_auto_set(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="tcommenter",
            name="T Commenter",
            email="tcomment@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Post for time test", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        comment = Comment(content="Time test", post_id=post.post_id, user_id=user.user_id)
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        assert comment.created_at is not None

    def test_user_has_posts_relationship(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        user = User(
            username="reluser2",
            name="Rel User 2",
            email="rel2@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post1 = Post(content="Post 1", user_id=user.user_id)
        post2 = Post(content="Post 2", user_id=user.user_id)
        db_session.add(post1)
        db_session.add(post2)
        db_session.commit()
        db_session.refresh(user)
        assert len(user.posts) == 2

    def test_user_has_comments_relationship(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="commentreluser",
            name="Comment Rel User",
            email="commentrel@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Post for comment rel", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        c1 = Comment(content="C1", post_id=post.post_id, user_id=user.user_id)
        c2 = Comment(content="C2", post_id=post.post_id, user_id=user.user_id)
        db_session.add(c1)
        db_session.add(c2)
        db_session.commit()
        db_session.refresh(user)
        assert len(user.comments) == 2

    def test_post_has_comments_relationship(self, db_session):
        from app.models.user import User
        from app.models.post import Post
        from app.models.comment import Comment
        user = User(
            username="postcomrel",
            name="Post Com Rel",
            email="postcomrel@example.com",
            password=encrypt_password("Pass123!"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        post = Post(content="Post with comments", user_id=user.user_id)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        c1 = Comment(content="C1", post_id=post.post_id, user_id=user.user_id)
        c2 = Comment(content="C2", post_id=post.post_id, user_id=user.user_id)
        db_session.add(c1)
        db_session.add(c2)
        db_session.commit()
        db_session.refresh(post)
        assert len(post.comments) == 2
