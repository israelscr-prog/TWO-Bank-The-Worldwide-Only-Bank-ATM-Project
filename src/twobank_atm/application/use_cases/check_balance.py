from dataclasses import dataclass
from uuid import UUID

from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.entities.transaction import Transaction

from twobank_atm.application.ports.repositories.account_repository import AccountRepository
from twobank_atm.application.ports.repositories.card_repository import CardRepository
from twobank_atm.application.ports.repositories.transaction_repository import TransactionRepository
from datetime import datetime, timezone


@dataclass
class CheckBalanceRequest:
    card_id: UUID
    pin: str


@dataclass
class CheckBalanceResponse:
    balance: Money


class CheckBalanceUseCase:
    """Returns the current balance for the account linked to a card."""

    def __init__(
        self,
        account_repo: AccountRepository,
        card_repo: CardRepository,
        tx_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._card_repo = card_repo
        self._tx_repo = tx_repo

    def execute(self, request: CheckBalanceRequest) -> CheckBalanceResponse:
        # 1. Load card and verify PIN (domain enforces PIN rules)
        card = self._card_repo.get_by_id(request.card_id)
        card.verify_pin(request.pin)
        self._card_repo.save(card)

        # 2. Load account
        account = self._account_repo.get_by_id(card.account_id)

        # 3. Record a BALANCE_INQUIRY transaction (optional but useful)
        tx = Transaction.record_balance_inquiry(
            account_id=account.id,
            atm_id=None,
        )
        self._tx_repo.add(tx)

        # 4. Build response DTO
        return CheckBalanceResponse(balance=account.balance)