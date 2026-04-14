"""
Domain exceptions — TWO Bank ATM.

En: All business-rule violations raise one of these exceptions.
ES: Todas las violaciones de reglas de negocio lanzan una de estas excepciones.

Author: TWO Bank Dev Team
Version: 0.1.0
"""


# ──────────────────────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────────────────────

class TWOBankError(Exception):
    """
    Base exception for all TWO Bank domain errors.
    Excepción base para todos los errores de dominio del TWO Bank.
    """
    def __init__(self, message: str = "An unexpected banking error occurred.") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


# ──────────────────────────────────────────────────────────────
# Account errors
# ──────────────────────────────────────────────────────────────

class InsufficientFundsError(TWOBankError):
    """Raised when an account does not have enough balance for an operation."""
    def __init__(self, requested: str = "", available: str = "") -> None:
        detail = f" (requested: {requested}, available: {available})" if requested else ""
        super().__init__(f"Insufficient funds.{detail}")


class AccountNotFoundError(TWOBankError):
    """Raised when an account cannot be found."""
    def __init__(self, account_id: str = "") -> None:
        detail = f": {account_id}" if account_id else ""
        super().__init__(f"Account not found{detail}.")


class AccountBlockedError(TWOBankError):
    """Raised when an operation is attempted on a blocked account."""
    def __init__(self) -> None:
        super().__init__("Account is blocked. Please contact your bank.")


# ──────────────────────────────────────────────────────────────
# Card errors
# ──────────────────────────────────────────────────────────────

class CardNotFoundError(TWOBankError):
    """Raised when a card cannot be found in the system."""
    def __init__(self, card_number: str = "") -> None:
        detail = f": {card_number}" if card_number else ""
        super().__init__(f"Card not found{detail}.")


class CardExpiredError(TWOBankError):
    """Raised when an expired card is used."""
    def __init__(self) -> None:
        super().__init__("Card is expired.")


class CardBlockedError(TWOBankError):
    """Raised when a blocked card is used."""
    def __init__(self) -> None:
        super().__init__("Card is blocked. Please contact your bank.")


# ──────────────────────────────────────────────────────────────
# PIN errors
# ──────────────────────────────────────────────────────────────

class InvalidPinError(TWOBankError):
    """Raised when an incorrect PIN is entered."""
    def __init__(self, attempts_left: int = 0) -> None:
        detail = f" {attempts_left} attempt(s) remaining." if attempts_left else ""
        super().__init__(f"Invalid PIN.{detail}")


class PinBlockedError(TWOBankError):
    """Raised when the PIN is blocked after too many failed attempts."""
    def __init__(self) -> None:
        super().__init__("PIN blocked after too many failed attempts. Contact your bank.")


# ──────────────────────────────────────────────────────────────
# ATM errors
# ──────────────────────────────────────────────────────────────

class ATMInsufficientCashError(TWOBankError):
    """Raised when the ATM does not have enough cash to dispense."""
    def __init__(self, requested: str = "") -> None:
        detail = f" (requested: {requested})" if requested else ""
        super().__init__(f"ATM has insufficient cash.{detail}")


class InvalidAmountError(TWOBankError):
    """Raised when an invalid withdrawal or deposit amount is given."""
    def __init__(self, reason: str = "") -> None:
        detail = f": {reason}" if reason else ""
        super().__init__(f"Invalid amount{detail}.")


class CurrencyMismatchError(TWOBankError):
    """Raised when two Money objects with different currencies are operated together."""
    def __init__(self, currency_a: str = "", currency_b: str = "") -> None:
        detail = f" ({currency_a} vs {currency_b})" if currency_a else ""
        super().__init__(f"Currency mismatch{detail}.")