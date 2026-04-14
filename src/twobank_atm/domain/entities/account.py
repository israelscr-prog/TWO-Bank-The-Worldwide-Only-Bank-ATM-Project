"""
Account entity — TWO Bank ATM.

EN: Represents a bank account with balance, currency and status.
ES: Representa una cuenta bancaria con saldo, divisa y estado.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currency import Currency
from twobank_atm.domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    AccountBlockedError,
)


class AccountStatus(Enum):
    """Possible states of a bank account."""
    ACTIVE  = "active"
    BLOCKED = "blocked"
    CLOSED  = "closed"


@dataclass
class Account:
    """
    Entity representing a bank account.

    Attributes:
        id:         Unique account identifier (UUID).
        owner_name: Full name of the account holder.
        balance:    Current balance as a Money value object.
        status:     Current account status (active/blocked/closed).
        created_at: Timestamp of account creation.
    """

    owner_name: str
    balance:    Money
    id:         UUID          = field(default_factory=uuid4)
    status:     AccountStatus = field(default=AccountStatus.ACTIVE)
    created_at: datetime      = field(default_factory=lambda: datetime.now(timezone.utc))

    # ──────────────────────────────────────────────
    # Factory
    # ──────────────────────────────────────────────
    @classmethod
    def open(cls, owner_name: str, currency: Currency, initial_deposit: Money | None = None) -> "Account":
        """
        Open a new bank account.

        Args:
            owner_name:      Full name of the account holder.
            currency:        Base currency of the account.
            initial_deposit: Optional opening balance (default: 0.00).

        Returns:
            New Account instance with ACTIVE status.

        Raises:
            ValueError: If owner_name is empty.
        """
        if not owner_name or not owner_name.strip():
            raise ValueError("owner_name cannot be empty.")

        opening_balance = initial_deposit or Money.of("0.00", currency)
        return cls(owner_name=owner_name.strip(), balance=opening_balance)

    # ──────────────────────────────────────────────
    # Core operations
    # ──────────────────────────────────────────────
    def deposit(self, amount: Money) -> None:
        """
        Add funds to the account.

        Args:
            amount: Amount to deposit. Must be > 0 and same currency.

        Raises:
            AccountBlockedError: If account is not active.
            InvalidAmountError:  If amount is zero or negative.
        """
        self._assert_active()
        self._assert_positive(amount)
        self.balance = self.balance.add(amount)

    def withdraw(self, amount: Money) -> None:
        """
        Deduct funds from the account.

        Args:
            amount: Amount to withdraw. Must be > 0, same currency, and <= balance.

        Raises:
            AccountBlockedError:   If account is not active.
            InsufficientFundsError: If balance is too low.
        """
        self._assert_active()
        self._assert_positive(amount)
        if amount.is_greater_than(self.balance):
            raise InsufficientFundsError(
                requested=str(amount),
                available=str(self.balance)
            )
        self.balance = self.balance.subtract(amount)

    def block(self) -> None:
        """Block the account. No operations allowed while blocked."""
        self.status = AccountStatus.BLOCKED

    def unblock(self) -> None:
        """Reactivate a blocked account."""
        self.status = AccountStatus.ACTIVE

    def close(self) -> None:
        """Permanently close the account."""
        self.status = AccountStatus.CLOSED

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────
    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    def has_sufficient_funds(self, amount: Money) -> bool:
        """Check if the account can cover a given amount."""
        return not amount.is_greater_than(self.balance)

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    def _assert_active(self) -> None:
        if self.status != AccountStatus.ACTIVE:
            raise AccountBlockedError()

    def _assert_positive(self, amount: Money) -> None:
        if amount.is_zero():
            raise ValueError("Amount must be greater than zero.")

    # ──────────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────────
    def __str__(self) -> str:
        return (
            f"Account({self.id}) | "
            f"{self.owner_name} | "
            f"Balance: {self.balance} | "
            f"Status: {self.status.value}"
        )