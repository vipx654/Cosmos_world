"""
===============================================================================
COSMOS Authentication Service

Business logic for user authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from domains.authentication.models import User
from domains.authentication.repositories import UserRepository
from core.security import hash_password

class AuthenticationService:
    """
    Business logic for authentication.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: str | None = None,
    ) -> User:

        if self.repository.get_by_username(username):
            raise ValueError("Username already exists.")

        if self.repository.get_by_email(email):
            raise ValueError("Email already exists.")
        hashed_password = hash_password(password_hash)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
        )

        return self.repository.create(user)

    def get_user(self, user_id: int):
        return self.repository.get_by_id(user_id)

    def get_by_username(self, username: str):
        return self.repository.get_by_username(username)