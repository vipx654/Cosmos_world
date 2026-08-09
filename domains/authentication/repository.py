"""
===============================================================================
COSMOS Authentication Repository

Database access layer for authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy.orm import Session

from domains.authentication.models import User


class UserRepository:
    """
    Handles all database operations related to User.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def list_users(self) -> list[User]:
        return (
            self.db.query(User)
            .order_by(User.id)
            .all()
        )

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()