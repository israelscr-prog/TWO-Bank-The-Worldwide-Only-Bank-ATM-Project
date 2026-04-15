from abc import abstractmethod
from typing import Protocol, runtime_checkable

from twobank_atm.domain.entities.transaction import Transaction


@runtime_checkable
class TransactionRepository(Protocol):
    """Port for persisting transactions."""

    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        """Store a new transaction in the log."""
        ...