import os
import pytest
from typing import Generator
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy import create_engine as sa_create_engine

os.environ["DATABASE_URI"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-12345"
os.environ["ENV"] = "test"

def _test_create_engine(url, **kwargs):
    if isinstance(url, str) and url.startswith("sqlite"):
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs.pop("pool_timeout", None)
        kwargs.pop("pool_recycle", None)
        connect_args = kwargs.pop("connect_args", {})
        connect_args["check_same_thread"] = False
        kwargs["connect_args"] = connect_args
    return sa_create_engine(url, **kwargs)

_patcher = patch("sqlmodel.create_engine", new=_test_create_engine)
_patcher.start()

from app.routers import templates, static_files, router, api_router
from app.database import get_session
from app.config import get_settings
from app.utilities.security import encrypt_password, create_access_token
from app.models.user import User


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(test_engine) -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    application = FastAPI(
        middleware=[Middleware(SessionMiddleware, secret_key="test-secret-key-12345")]
    )
    application.include_router(router)
    application.include_router(api_router)
    application.mount("/static", static_files, name="static")

    @application.exception_handler(status.HTTP_401_UNAUTHORIZED)
    async def unauthorized_redirect_handler(request: Request, exc: Exception):
        if request.url.path.startswith("/api"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized"})
        return templates.TemplateResponse(request=request, name="401.html")

    return application


@pytest.fixture(name="client")
def client_fixture(app: FastAPI, session: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user_data")
def test_user_data_fixture():
    return {
        "username": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "role": "regular_user",
    }


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session, test_user_data: dict) -> User:
    user = User(
        username=test_user_data["username"],
        name=test_user_data["name"],
        email=test_user_data["email"],
        password=encrypt_password(test_user_data["password"]),
        role=test_user_data["role"],
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_admin")
def test_admin_fixture(session: Session) -> User:
    user = User(
        username="admin",
        name="Admin User",
        email="admin@example.com",
        password=encrypt_password("AdminPass123!"),
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user_token")
def user_token_fixture(test_user: User) -> str:
    return create_access_token(data={"sub": f"{test_user.user_id}", "role": test_user.role})


@pytest.fixture(name="admin_token")
def admin_token_fixture(test_admin: User) -> str:
    return create_access_token(data={"sub": f"{test_admin.user_id}", "role": test_admin.role})


@pytest.fixture(name="authorized_client")
def authorized_client_fixture(client: TestClient, user_token: str) -> TestClient:
    client.cookies.set("access_token", user_token)
    return client


@pytest.fixture(name="admin_client")
def admin_client_fixture(client: TestClient, admin_token: str) -> TestClient:
    client.cookies.set("access_token", admin_token)
    return client
