from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies
from twobank_atm.domain.entities.transaction import Transaction

from twobank_atm.application.ports.repositories.account_repository import AccountRepository
from twobank_atm.application.ports.repositories.card_repository import CardRepository
from twobank_atm.application.ports.repositories.transaction_repository import TransactionRepository


@dataclass
class TransferFundsRequest:
    card_id: UUID
    pin: str
    from_account_id: UUID
    to_account_id: UUID
    amount: float
    currency_code: str = "EUR"


@dataclass
class TransferFundsResponse:
    transaction_id: UUID
    from_account_balance: Money
    to_account_balance: Money


class TransferFundsUseCase:
    """Transfers money between two accounts."""

    def __init__(
        self,
        account_repo: AccountRepository,
        card_repo: CardRepository,
        tx_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._card_repo = card_repo
        self._tx_repo = tx_repo

    def execute(self, request: TransferFundsRequest) -> TransferFundsResponse:
        # 1. Authenticate via card + PIN
        card = self._card_repo.get_by_id(request.card_id)
        card.verify_pin(request.pin)
        self._card_repo.save(card)

        # 2. Load accounts
        from_account = self._account_repo.get_by_id(request.from_account_id)
        to_account = self._account_repo.get_by_id(request.to_account_id)

        # 3. Build Money
        currency = Currencies.from_code(request.currency_code)
        amount = Money.of(request.amount, currency)

        # 4. Withdraw from source account (domain checks funds, status, etc.)
        from_account.withdraw(amount)
        self._account_repo.save(from_account)

        # 5. Deposit into destination account
        to_account.deposit(amount)
        self._account_repo.save(to_account)

        # 6. Record transfer transaction
        transaction = Transaction.record_transfer(
            account_id=from_account.id,
            amount=amount,
            atm_id=None,
            to_account_id=to_account.id,
        )
        self._tx_repo.add(transaction)

        # 7. Response DTO
        return TransferFundsResponse(
            transaction_id=transaction.id,
            from_account_balance=from_account.balance,
            to_account_balance=to_account.balance,
        )