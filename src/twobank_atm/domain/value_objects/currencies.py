"""
Predefined currencies for TWO Bank ATM.
Divisas predefinidas del cajero TWO Bank.

Usage:
    from src.domain.value_objects.currencies import Currencies
    eur = Currencies.EUR

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from twobank_atm.domain.value_objects.currency import Currency


class Currencies:
    """Catalog of all currencies supported by TWO Bank ATM."""

    # ── Fiat ──────────────────────────────────────
    EUR = Currency(code="EUR", symbol="€",  name="Euro")
    USD = Currency(code="USD", symbol="$",  name="US Dollar")
    GBP = Currency(code="GBP", symbol="£",  name="British Pound")
    JPY = Currency(code="JPY", symbol="¥",  name="Japanese Yen")
    CHF = Currency(code="CHF", symbol="₣",  name="Swiss Franc")

    # ── Crypto ────────────────────────────────────
    BTC = Currency(code="BTC", symbol="₿",  name="Bitcoin")

    # ── All as list (useful for menus / validation)
    ALL: list[Currency] = [EUR, USD, GBP, JPY, CHF, BTC]

    @classmethod
    def from_code(cls, code: str) -> Currency:
        """
        Retrieve a Currency by its ISO code.

        Args:
            code: ISO 4217 code (case-insensitive, e.g. 'eur', 'USD').

        Returns:
            Matching Currency instance.

        Raises:
            ValueError: If the code is not supported.
        """
        normalized = code.upper()
        for currency in cls.ALL:
            if currency.code == normalized:
                return currency
        raise ValueError(f"Unsupported currency code: {code!r}")