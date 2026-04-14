"""
Money value object — TWO Bank ATM.

EN: Represents an immutable monetary amount with its currency.
ES: Inmutable cantidad monetaria con su divisa.

Author: Isra C. Rojas (TWO Bank Dev Team)
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Union

from twobank_atm.domain.value_objects.currency import Currency


@dataclass(frozen=True)
class Money:
    """
    Immutable value object representing an amount of money.

    Attributes:
        amount: Decimal — exact monetary amount (always >= 0).
        currency: Currency — the currency of this amount.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal.")
        if self.amount < Decimal("0"):
            raise ValueError("amount cannot be negative.")
        if not isinstance(self.currency, Currency):
            raise TypeError("currency must be a Currency instance.")

    # ──────────────────────────────────────────────
    # Factory
    # ──────────────────────────────────────────────
    @classmethod
    def of(cls, amount: Union[str, int, float, Decimal], currency: Currency) -> "Money":
        """
        Safe factory — converts any numeric type to Decimal.

        Args:
            amount: Numeric value (str recommended for precision).
            currency: Currency of the amount.

        Returns:
            New Money instance.

        Raises:
            ValueError: If amount string is malformed or negative.
        """
        try:
            decimal_amount = Decimal(str(amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except InvalidOperation as exc:
            raise ValueError(f"Invalid amount: {amount!r}") from exc

        return cls(amount=decimal_amount, currency=currency)

    # ──────────────────────────────────────────────
    # Arithmetic
    # ──────────────────────────────────────────────
    def add(self, other: "Money") -> "Money":
        """Add two Money amounts. Currencies must match."""
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Subtract other from self. Result cannot be negative."""
        self._assert_same_currency(other)
        result = self.amount - other.amount
        if result < Decimal("0"):
            raise ValueError("Subtraction would result in a negative amount.")
        return Money(amount=result, currency=self.currency)

    def multiply(self, factor: Union[int, Decimal]) -> "Money":
        """Multiply amount by a scalar factor."""
        result = (self.amount * Decimal(str(factor))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return Money(amount=result, currency=self.currency)

    # ──────────────────────────────────────────────
    # Comparison
    # ──────────────────────────────────────────────
    def is_greater_than(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def is_less_than(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount < other.amount

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    # ──────────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────────
    def __str__(self) -> str:
        return f"{self.currency.symbol}{self.amount:,.2f}"

    def __repr__(self) -> str:
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: {self.currency.code} vs {other.currency.code}"
            )