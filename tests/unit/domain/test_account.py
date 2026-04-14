"""Tests for Account entity."""
import pytest
from twobank_atm.domain.entities.account import Account, AccountStatus
from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies
from twobank_atm.domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    AccountBlockedError,
)

EUR = Currencies.EUR


def make_account(balance: str = "1000") -> Account:
    return Account.open(
        owner_name="María García",
        currency=EUR,
        initial_deposit=Money.of(balance, EUR),
    )


class TestAccountCreation:
    def test_open_account(self):
        acc = make_account()
        assert acc.owner_name == "María García"
        assert acc.is_active()

    def test_empty_owner_raises(self):
        with pytest.raises(ValueError):
            Account.open(owner_name="", currency=EUR)

    def test_default_zero_balance(self):
        acc = Account.open(owner_name="Juan", currency=EUR)
        assert acc.balance.is_zero()


class TestAccountDeposit:
    def test_deposit_increases_balance(self):
        acc = make_account("500")
        acc.deposit(Money.of("200", EUR))
        assert acc.balance == Money.of("700", EUR)

    def test_deposit_on_blocked_account_raises(self):
        acc = make_account()
        acc.block()
        with pytest.raises(AccountBlockedError):
            acc.deposit(Money.of("100", EUR))

    def test_deposit_zero_raises(self):
        acc = make_account()
        with pytest.raises(ValueError):
            acc.deposit(Money.of("0", EUR))


class TestAccountWithdraw:
    def test_withdraw_decreases_balance(self):
        acc = make_account("1000")
        acc.withdraw(Money.of("300", EUR))
        assert acc.balance == Money.of("700", EUR)

    def test_withdraw_entire_balance(self):
        acc = make_account("500")
        acc.withdraw(Money.of("500", EUR))
        assert acc.balance.is_zero()

    def test_withdraw_insufficient_funds_raises(self):
        acc = make_account("100")
        with pytest.raises(InsufficientFundsError):
            acc.withdraw(Money.of("500", EUR))

    def test_withdraw_on_blocked_account_raises(self):
        acc = make_account()
        acc.block()
        with pytest.raises(AccountBlockedError):
            acc.withdraw(Money.of("100", EUR))


class TestAccountStatus:
    def test_block_and_unblock(self):
        acc = make_account()
        acc.block()
        assert acc.status == AccountStatus.BLOCKED
        acc.unblock()
        assert acc.is_active()

    def test_close_account(self):
        acc = make_account()
        acc.close()
        assert acc.status == AccountStatus.CLOSED