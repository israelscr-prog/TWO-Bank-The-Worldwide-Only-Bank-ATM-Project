from typing import Dict
from uuid import UUID

from twobank_atm.domain.entities.card import Card
from twobank_atm.domain.exceptions.domain_exceptions import CardNotFoundError
from twobank_atm.application.ports.repositories.card_repository import CardRepository


class InMemoryCardRepository(CardRepository):
    def __init__(self) -> None:
        self._storage: Dict[UUID, Card] = {}

    def get_by_id(self, card_id: UUID) -> Card:
        try:
            return self._storage[card_id]
        except KeyError as exc:
            raise CardNotFoundError(f"Card {card_id} not found.") from exc

    def save(self, card: Card) -> None:
        self._storage[card.id] = card

    def add(self, card: Card) -> None:
        self.save(card)

    def clear(self) -> None:
        self._storage.clear()