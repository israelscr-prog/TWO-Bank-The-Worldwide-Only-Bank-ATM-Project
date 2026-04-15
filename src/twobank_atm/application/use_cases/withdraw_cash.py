from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies
from twobank_atm.domain.entities.transaction import Transaction

from twobank_atm.application.ports.repositories.account_repository import AccountRepository
from twobank_atm.application.ports.repositories.card_repository import CardRepository
from twobank_atm.application.ports.repositories.atm_repository import ATMRepository
from twobank_atm.application.ports.repositories.transaction_repository import TransactionRepository


@dataclass
class WithdrawCashRequest:
    atm_id: UUID
    card_id: UUID
    pin: str
    amount: float
    currency_code: str = "EUR"


@dataclass
class WithdrawCashResponse:
    transaction_id: UUID
    dispensed_notes: dict[int, int]
    remaining_balance: Money


class WithdrawCashUseCase:
    """Orchestrates a complete ATM cash withdrawal."""

    def __init__(
        self,
        account_repo: AccountRepository,
        card_repo: CardRepository,
        atm_repo: ATMRepository,
        tx_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._card_repo = card_repo
        self._atm_repo = atm_repo
        self._tx_repo = tx_repo

    def execute(self, request: WithdrawCashRequest) -> WithdrawCashResponse:
        # 1. Load card and verify PIN
        card = self._card_repo.get_by_id(request.card_id)
        card.verify_pin(request.pin)
        self._card_repo.save(card)

        # 2. Load account and ATM
        account = self._account_repo.get_by_id(card.account_id)
        atm = self._atm_repo.get_by_id(request.atm_id)

        # 3. Build Money from request
        currency = Currencies.from_code(request.currency_code)
        amount = Money.of(request.amount, currency)

        # 4. Withdraw from account (domain applies business rules)
        account.withdraw(amount)
        self._account_repo.save(account)

        # 5. Dispense cash from ATM
        dispensed_notes = atm.dispense_cash(amount)
        self._atm_repo.save(atm)

        # 6. Record transaction
        transaction = Transaction.record_withdrawal(
            account_id=account.id,
            amount=amount,
            atm_id=atm.id,
        )
        self._tx_repo.add(transaction)

        # 7. Build response DTO
        return WithdrawCashResponse(
            transaction_id=transaction.id,
            dispensed_notes=dispensed_notes,
            remaining_balance=account.balance,
        )