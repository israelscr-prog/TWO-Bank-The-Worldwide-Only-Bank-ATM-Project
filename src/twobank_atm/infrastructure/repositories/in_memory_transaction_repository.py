from typing import List
from uuid import UUID

from twobank_atm.domain.entities.transaction import Transaction
from twobank_atm.application.ports.repositories.transaction_repository import TransactionRepository


class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self) -> None:
        self._log: List[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        self._log.append(transaction)

    def get_all(self) -> List[Transaction]:
        return list(self._log)

    def get_by_account(self, account_id: UUID) -> List[Transaction]:
        return [tx for tx in self._log if tx.account_id == account_id]

    def clear(self) -> None:
        self._log.clear()