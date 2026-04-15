from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from twobank_atm.domain.entities.user import User


@runtime_checkable
class UserRepository(Protocol):
    """Port for loading and saving User aggregates."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User:
        """Return the user or raise a not-found error."""
        ...

    @abstractmethod
    def save(self, user: User) -> None:
        """Persist changes to the given user."""
        ...