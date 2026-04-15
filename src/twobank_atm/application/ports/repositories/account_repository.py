from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from twobank_atm.domain.entities.account import Account


@runtime_checkable
class AccountRepository(Protocol):
    """Port for loading and saving Account aggregates."""

    @abstractmethod
    def get_by_id(self, account_id: UUID) -> Account:
        """Return the account or raise AccountNotFoundError."""
        ...

    @abstractmethod
    def save(self, account: Account) -> None:
        """Persist changes to the given account."""
        ...