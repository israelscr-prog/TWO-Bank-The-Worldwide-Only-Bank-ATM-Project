from typing import Dict
from uuid import UUID

from twobank_atm.domain.entities.user import User
from twobank_atm.domain.exceptions.domain_exceptions import TWOBankError
from twobank_atm.application.ports.repositories.user_repository import UserRepository


class UserNotFoundError(TWOBankError):
    pass


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._storage: Dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> User:
        try:
            return self._storage[user_id]
        except KeyError as exc:
            raise UserNotFoundError(f"User {user_id} not found.") from exc

    def save(self, user: User) -> None:
        self._storage[user.id] = user

    def add(self, user: User) -> None:
        self.save(user)

    def clear(self) -> None:
        self._storage.clear()