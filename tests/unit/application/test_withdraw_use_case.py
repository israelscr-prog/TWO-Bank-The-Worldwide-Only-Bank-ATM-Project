import pytest
from datetime import date
from uuid import uuid4

from twobank_atm.domain.entities.account import Account, AccountStatus
from twobank_atm.domain.entities.card import Card, CardStatus
from twobank_atm.domain.entities.atm_machine import ATMMachine, ATMStatus
from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies
from twobank_atm.domain.value_objects.pin import Pin
from twobank_atm.domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    InvalidPinError,
    PinBlockedError,
    CardBlockedError,
    ATMInsufficientCashError,
)

from twobank_atm.application.use_cases.withdraw_cash import (
    WithdrawCashUseCase,
    WithdrawCashRequest,
)
from twobank_atm.infrastructure.repositories.in_memory_account_repository import InMemoryAccountRepository
from twobank_atm.infrastructure.repositories.in_memory_card_repository import InMemoryCardRepository
from twobank_atm.infrastructure.repositories.in_memory_atm_repository import InMemoryATMRepository
from twobank_atm.infrastructure.repositories.in_memory_transaction_repository import InMemoryTransactionRepository


EUR = Currencies.from_code("EUR")
RAW_PIN = "1234"


# ─── helpers ────────────────────────────────────────────────────────────────

def make_account(balance: float = 500.0) -> Account:
    account = Account.open(
        owner_name="Isra ",
        currency=EUR,
        initial_deposit=Money.of(balance, EUR),
    )
    return account


def make_card(account_id, raw_pin: str = RAW_PIN) -> Card:
    return Card.issue(
        card_number="4111111111111234",
        account_id=account_id,
        raw_pin=raw_pin,
        expiry_date=date(2030, 12, 31),
    )


def make_atm() -> ATMMachine:
    return ATMMachine.install(
        location="Vigo Branch",
        currency=EUR,
        initial_cash={50: 10, 20: 20, 10: 30},
    )


# ─── fixture ────────────────────────────────────────────────────────────────

@pytest.fixture
def repos():
    account_repo = InMemoryAccountRepository()
    card_repo    = InMemoryCardRepository()
    atm_repo     = InMemoryATMRepository()
    tx_repo      = InMemoryTransactionRepository()

    account = make_account(balance=500.0)
    card    = make_card(account_id=account.id)
    atm     = make_atm()

    account_repo.add(account)
    card_repo.add(card)
    atm_repo.add(atm)

    return {
        "account_repo": account_repo,
        "card_repo":    card_repo,
        "atm_repo":     atm_repo,
        "tx_repo":      tx_repo,
        "account":      account,
        "card":         card,
        "atm":          atm,
    }


def make_use_case(repos) -> WithdrawCashUseCase:
    return WithdrawCashUseCase(
        account_repo=repos["account_repo"],
        card_repo=repos["card_repo"],
        atm_repo=repos["atm_repo"],
        tx_repo=repos["tx_repo"],
    )


# ─── tests ──────────────────────────────────────────────────────────────────

class TestWithdrawCashSuccess:

    def test_balance_decreases(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=100.0,
        )
        response = use_case.execute(request)

        account = repos["account_repo"].get_by_id(repos["account"].id)
        assert account.balance == Money.of(400.0, EUR)

    def test_response_has_correct_remaining_balance(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=100.0,
        )
        response = use_case.execute(request)
        assert response.remaining_balance == Money.of(400.0, EUR)

    def test_dispensed_notes_correct(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=170.0,
        )
        response = use_case.execute(request)
        assert response.dispensed_notes == {50: 3, 20: 1}

    def test_transaction_recorded(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=100.0,
        )
        use_case.execute(request)
        txs = repos["tx_repo"].get_all()
        assert len(txs) == 1
        assert txs[0].amount == Money.of(100.0, EUR)


class TestWithdrawCashFailures:

    def test_wrong_pin_raises(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin="9999",
            amount=100.0,
        )
        with pytest.raises(InvalidPinError):
            use_case.execute(request)

    def test_insufficient_funds_raises(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=9999.0,
        )
        with pytest.raises(InsufficientFundsError):
            use_case.execute(request)

    def test_atm_no_cash_raises(self, repos):
        # Vaciar el cajero
        atm = repos["atm"]
        atm.cash_inventory = {50: 0, 20: 0, 10: 0}
        repos["atm_repo"].save(atm)

        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=atm.id,
            card_id=repos["card"].id,
            pin=RAW_PIN,
            amount=50.0,
        )
        with pytest.raises(ATMInsufficientCashError):
            use_case.execute(request)

    def test_three_wrong_pins_block_card(self, repos):
        use_case = make_use_case(repos)
        request = WithdrawCashRequest(
            atm_id=repos["atm"].id,
            card_id=repos["card"].id,
            pin="9999",
            amount=100.0,
        )
        for _ in range(2):
            with pytest.raises(InvalidPinError):
                use_case.execute(request)

        with pytest.raises(PinBlockedError):
            use_case.execute(request)

        with pytest.raises(CardBlockedError):
            use_case.execute(request)

    