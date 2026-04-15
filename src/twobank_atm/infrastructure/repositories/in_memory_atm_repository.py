from typing import Dict
from uuid import UUID

from twobank_atm.domain.entities.atm_machine import ATMMachine
from twobank_atm.domain.exceptions.domain_exceptions import TWOBankError
from twobank_atm.application.ports.repositories.atm_repository import ATMRepository


class ATMNotFoundError(TWOBankError):
    pass


class InMemoryATMRepository(ATMRepository):
    def __init__(self) -> None:
        self._storage: Dict[UUID, ATMMachine] = {}

    def get_by_id(self, atm_id: UUID) -> ATMMachine:
        try:
            return self._storage[atm_id]
        except KeyError as exc:
            raise ATMNotFoundError(f"ATM {atm_id} not found.") from exc

    def save(self, atm: ATMMachine) -> None:
        self._storage[atm.id] = atm

    def add(self, atm: ATMMachine) -> None:
        self.save(atm)

    def clear(self) -> None:
        self._storage.clear()