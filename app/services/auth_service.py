from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.models.user import User
from typing import Optional

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(plaintext_password=password, encrypted_password=user.password):
            return None
        access_token = create_access_token(data={"sub": f"{user.user_id}", "role": user.role})
        return access_token

    def register_user(self, username: str, email: str, password: str):
        if not username or not username.strip():
            raise ValueError("Username is required")
        new_user = User(
            username=username,
            name=username,
            email=email,
            password=encrypt_password(password),
            role="regular_user",
        )
        return self.user_repo.create(new_user)
