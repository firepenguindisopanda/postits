import pytest
from fastapi import status


def _assert_redirect_or_validation(response, valid_codes=None):
    if valid_codes is None:
        valid_codes = {303, 307, 422}
    assert response.status_code in valid_codes, f"Got {response.status_code}, expected one of {valid_codes}"


class TestIndexRoute:
    def test_index_redirects_to_login_when_not_logged_in(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/login" in location

    def test_index_redirects_to_app_when_logged_in(self, authorized_client):
        response = authorized_client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/app" in location

    def test_index_redirects_to_admin_when_admin(self, admin_client):
        response = admin_client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/admin" in location


class TestLoginRoute:
    def test_login_page_returns_html(self, client):
        response = client.get("/login")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/html")

    def test_login_valid_credentials(self, client, test_user_data):
        response = client.post(
            "/login",
            data={"username": test_user_data["username"], "password": test_user_data["password"]},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "access_token" in response.cookies

    def test_login_invalid_password(self, client):
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "wrongpassword"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/login" in location

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/login",
            data={"username": "nobody", "password": "SomePass123!"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/login" in location

    def test_login_empty_fields(self, client):
        response = client.post(
            "/login",
            data={"username": "", "password": ""},
            follow_redirects=False,
        )
        assert response.status_code in (status.HTTP_303_SEE_OTHER, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestRegisterRoute:
    def test_register_page_returns_html(self, client):
        response = client.get("/register")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/html")

    def test_register_new_user(self, client):
        response = client.post(
            "/register",
            data={
                "username": "brandnew",
                "email": "brandnew@example.com",
                "password": "BrandNewPass123!",
            },
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/login" in location

    def test_register_duplicate_username(self, client, test_user_data):
        response = client.post(
            "/register",
            data={
                "username": test_user_data["username"],
                "email": "other@example.com",
                "password": "SomePass123!",
            },
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/register" in location

    def test_register_duplicate_email(self, client, test_user_data):
        response = client.post(
            "/register",
            data={
                "username": "anotheruser",
                "email": test_user_data["email"],
                "password": "SomePass123!",
            },
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_register_empty_fields(self, client):
        response = client.post(
            "/register",
            data={"username": "", "email": "", "password": ""},
            follow_redirects=False,
        )
        _assert_redirect_or_validation(response)


class TestLogoutRoute:
    def test_logout_clears_token(self, client, user_token):
        client.cookies.set("access_token", user_token)
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers.get("location", "")
        assert "/login" in location
        set_cookie = response.headers.get("set-cookie", "")
        assert "access_token=" in set_cookie or "access_token" in set_cookie.lower()


class TestUserAppRoute:
    def test_user_home_requires_auth(self, client):
        response = client.get("/app", follow_redirects=False)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_user_home_returns_html_for_auth_user(self, authorized_client):
        response = authorized_client.get("/app")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/html")


class TestAdminRoute:
    def test_admin_requires_admin_role(self, authorized_client):
        response = authorized_client.get("/admin", follow_redirects=False)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_admin_returns_html_for_admin(self, admin_client):
        response = admin_client.get("/admin")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/html")


class TestUsersAPI:
    def test_list_users_empty(self, client):
        response = client.get("/api/users")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_users_with_data(self, client, test_user):
        response = client.get("/api/users")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1


class TestPostRoutes:
    def test_create_post_api(self, authorized_client):
        response = authorized_client.post(
            "/api/posts",
            json={"content": "Test post via API"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Test post via API"

    def test_list_posts(self, authorized_client):
        authorized_client.post("/api/posts", json={"content": "Post 1"})
        authorized_client.post("/api/posts", json={"content": "Post 2"})
        response = authorized_client.get("/api/posts")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

    def test_get_post_by_id(self, authorized_client):
        create_resp = authorized_client.post("/api/posts", json={"content": "Find me"})
        post_id = create_resp.json()["post_id"]
        response = authorized_client.get(f"/api/posts/{post_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["content"] == "Find me"

    def test_get_post_not_found(self, authorized_client):
        response = authorized_client.get("/api/posts/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_post(self, authorized_client):
        create_resp = authorized_client.post("/api/posts", json={"content": "Delete me"})
        post_id = create_resp.json()["post_id"]
        response = authorized_client.delete(f"/api/posts/{post_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        get_resp = authorized_client.get(f"/api/posts/{post_id}")
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_create_post_unauthenticated(self, client):
        response = client.post("/api/posts", json={"content": "No auth"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCommentRoutes:
    def test_create_comment_api(self, authorized_client):
        post_resp = authorized_client.post("/api/posts", json={"content": "Post for comment"})
        post_id = post_resp.json()["post_id"]
        response = authorized_client.post(
            "/api/comments",
            json={"content": "Nice post!", "post_id": post_id},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Nice post!"

    def test_list_comments_for_post(self, authorized_client):
        post_resp = authorized_client.post("/api/posts", json={"content": "Comment post"})
        post_id = post_resp.json()["post_id"]
        authorized_client.post("/api/comments", json={"content": "C1", "post_id": post_id})
        authorized_client.post("/api/comments", json={"content": "C2", "post_id": post_id})
        response = authorized_client.get(f"/api/posts/{post_id}/comments")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_delete_comment(self, authorized_client):
        post_resp = authorized_client.post("/api/posts", json={"content": "Post"})
        post_id = post_resp.json()["post_id"]
        comment_resp = authorized_client.post(
            "/api/comments", json={"content": "Delete this", "post_id": post_id}
        )
        comment_id = comment_resp.json()["comment_id"]
        response = authorized_client.delete(f"/api/comments/{comment_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_comment_unauthenticated(self, client):
        response = client.post(
            "/api/comments",
            json={"content": "No auth", "post_id": 1},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
