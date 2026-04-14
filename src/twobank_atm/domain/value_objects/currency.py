"""
Currency value object — TWO Bank ATM.

EN: Represents an immutable currency (code, symbol, name).
ES: Divisa inmutable con código ISO, símbolo y nombre.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    """
    Immutable value object representing a currency.

    Attributes:
        code:   ISO 4217 currency code  (e.g. 'EUR', 'USD', 'BTC').
        symbol: Display symbol          (e.g. '€', '$', '₿').
        name:   Full currency name      (e.g. 'Euro', 'US Dollar').
    """

    code: str
    symbol: str
    name: str

    def __post_init__(self) -> None:
        if not self.code or not isinstance(self.code, str):
            raise ValueError("code must be a non-empty string.")
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("symbol must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string.")
        # Normalize code to uppercase (EUR, not eur)
        object.__setattr__(self, "code", self.code.upper())

    def __str__(self) -> str:
        return f"{self.symbol} ({self.code})"

    def __repr__(self) -> str:
        return f"Currency(code={self.code!r}, symbol={self.symbol!r}, name={self.name!r})"