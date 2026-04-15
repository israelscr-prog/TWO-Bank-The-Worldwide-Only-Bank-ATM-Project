from abc import ABC, abstractmethod
from uuid import UUID
from typing import Protocol, runtime_checkable

from twobank_atm.domain.entities.card import Card


@runtime_checkable
class CardRepository(Protocol):
    """Port for loading and saving Card aggregates."""

    @abstractmethod
    def get_by_id(self, card_id: UUID) -> Card:
        """Return the card or raise CardNotFoundError."""

    @abstractmethod
    def save(self, card: Card) -> None:
        """Persist changes to the given card."""