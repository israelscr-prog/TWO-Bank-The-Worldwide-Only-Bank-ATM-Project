from typing import Dict
from uuid import UUID

from twobank_atm.domain.entities.account import Account
from twobank_atm.domain.exceptions.domain_exceptions import AccountNotFoundError
from twobank_atm.application.ports.repositories.account_repository import AccountRepository


class InMemoryAccountRepository(AccountRepository):
    def __init__(self) -> None:
        self._storage: Dict[UUID, Account] = {}

    def get_by_id(self, account_id: UUID) -> Account:
        try:
            return self._storage[account_id]
        except KeyError as exc:
            raise AccountNotFoundError(f"Account {account_id} not found.") from exc

    def save(self, account: Account) -> None:
        self._storage[account.id] = account

    def add(self, account: Account) -> None:
        self.save(account)

    def clear(self) -> None:
        self._storage.clear()