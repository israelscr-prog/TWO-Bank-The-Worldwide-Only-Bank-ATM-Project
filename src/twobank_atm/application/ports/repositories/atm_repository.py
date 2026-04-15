from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from twobank_atm.domain.entities.atm_machine import ATMMachine


@runtime_checkable
class ATMRepository(Protocol):
    """Port for loading and saving ATMMachine aggregates."""

    @abstractmethod
    def get_by_id(self, atm_id: UUID) -> ATMMachine:
        """Return the ATM or raise a not-found error."""
        ...

    @abstractmethod
    def save(self, atm: ATMMachine) -> None:
        """Persist changes to the given ATM."""
        ...