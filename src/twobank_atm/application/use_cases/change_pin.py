from dataclasses import dataclass
from uuid import UUID

from twobank_atm.domain.value_objects.pin import Pin
from twobank_atm.domain.entities.transaction import Transaction
from twobank_atm.domain.value_objects.currencies import Currencies

from twobank_atm.application.ports.repositories.card_repository import CardRepository
from twobank_atm.application.ports.repositories.transaction_repository import TransactionRepository


@dataclass
class ChangePinRequest:
    card_id: UUID
    old_pin: str
    new_pin: str


@dataclass
class ChangePinResponse:
    card_id: UUID


class ChangePinUseCase:
    """Changes the PIN of a card after verifying the old PIN."""

    def __init__(
        self,
        card_repo: CardRepository,
        tx_repo: TransactionRepository,
    ) -> None:
        self._card_repo = card_repo
        self._tx_repo = tx_repo

    def execute(self, request: ChangePinRequest) -> ChangePinResponse:
        # 1. Load card and verify old PIN
        card = self._card_repo.get_by_id(request.card_id)
        card.verify_pin(request.old_pin)

        # 2. Set new PIN value object
        card.pin = Pin.create(request.new_pin)
        self._card_repo.save(card)

        # 3. Record PIN_CHANGE transaction
        tx = Transaction.record_pin_change(
            account_id=card.account_id,
            atm_id=None,
        )
        self._tx_repo.add(tx)

        return ChangePinResponse(card_id=card.id)