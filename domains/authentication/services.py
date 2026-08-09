"""
===============================================================================
COSMOS Authentication Service

Business logic for authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from domains.authentication.models import User
from domains.authentication.repository import UserRepository
from domains.authentication.security import hash_password
from domains.authentication.security import verify_password

from domains.license.services import LicenseService


class AuthenticationService:
    """
    Authentication business logic.
    """

    def __init__(
        self,
        repository: UserRepository,
        license_service: LicenseService,
    ):
        self.repository = repository
        self.license_service = license_service

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------

    def register(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> User:

        if self.repository.get_by_username(username):
            raise ValueError("Username already exists.")

        if self.repository.get_by_email(email):
            raise ValueError("Email already exists.")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        user = self.repository.create(user)

        # Create FREE license automatically
        self.license_service.create_license(
            user_id=user.id,
            license_type="FREE",
            max_devices=1,
        )

        return user

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> User:

        user = self.repository.get_by_username(username)

        if user is None:
            raise ValueError("Invalid username or password.")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid username or password.")

        return user

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_user(
        self,
        user_id: int,
    ) -> User | None:

        return self.repository.get_by_id(user_id)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:

        return self.repository.get_by_username(username)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return self.repository.get_by_email(email)