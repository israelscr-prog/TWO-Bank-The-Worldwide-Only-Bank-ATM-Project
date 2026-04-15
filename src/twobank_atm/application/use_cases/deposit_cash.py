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
class DepositCashRequest:
    atm_id: UUID
    card_id: UUID
    pin: str
    amount: float
    currency_code: str = "EUR"


@dataclass
class DepositCashResponse:
    transaction_id: UUID
    new_balance: Money


class DepositCashUseCase:
    """Deposits cash into the account linked to a card."""

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

    def execute(self, request: DepositCashRequest) -> DepositCashResponse:
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

        # 4. Deposit into account (domain rules)
        account.deposit(amount)
        self._account_repo.save(account)

        # 5. Update ATM inventory (dominio; aquí asumimos load_cash con un solo billete)
        atm.load_cash(int(amount.amount), 1)
        self._atm_repo.save(atm)

        # 6. Record transaction
        transaction = Transaction.record_deposit(
            account_id=account.id,
            amount=amount,
            atm_id=atm.id,
        )
        self._tx_repo.add(transaction)

        # 7. Response
        return DepositCashResponse(
            transaction_id=transaction.id,
            new_balance=account.balance,
        )