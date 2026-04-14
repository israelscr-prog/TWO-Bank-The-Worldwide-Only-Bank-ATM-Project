"""
Pin value object — TWO Bank ATM.

En: Stores a hashed PIN. The raw PIN is never retained after creation.
ES: Almacena el PIN hasheado. El PIN en texto plano nunca se conserva.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
import hashlib
import secrets
from dataclasses import dataclass, field


_PIN_LENGTH = 4  # Standard ATM PIN length


@dataclass(frozen=True)
class Pin:
    """
    Immutable value object representing a hashed ATM PIN.

    Attributes:
        _hashed_pin: SHA-256 hash of the raw PIN (never the raw value).
        _salt:       Random salt used during hashing.
    """

    _hashed_pin: str = field(repr=False)
    _salt: str       = field(repr=False)

    # ──────────────────────────────────────────────
    # Factory — the ONLY way to create a Pin
    # ──────────────────────────────────────────────
    @classmethod
    def create(cls, raw_pin: str) -> "Pin":
        """
        Create a Pin from a raw string. Raw value is discarded immediately.

        Args:
            raw_pin: 4-digit numeric string (e.g. '1234').

        Returns:
            New Pin instance with hashed value.

        Raises:
            ValueError: If PIN is not exactly 4 numeric digits.
        """
        cls._validate_raw(raw_pin)
        salt = secrets.token_hex(16)
        hashed = cls._hash(raw_pin, salt)
        return cls(_hashed_pin=hashed, _salt=salt)

    # ──────────────────────────────────────────────
    # Verification
    # ──────────────────────────────────────────────
    def verify(self, raw_pin: str) -> bool:
        """
        Check if a raw PIN matches this stored Pin.

        Args:
            raw_pin: PIN entered by the user.

        Returns:
            True if correct, False otherwise.
        """
        return secrets.compare_digest(
            self._hashed_pin,
            self._hash(raw_pin, self._salt)
        )

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    @staticmethod
    def _validate_raw(raw_pin: str) -> None:
        if not isinstance(raw_pin, str):
            raise ValueError("PIN must be a string.")
        if len(raw_pin) != _PIN_LENGTH:
            raise ValueError(f"PIN must be exactly {_PIN_LENGTH} digits.")
        if not raw_pin.isdigit():
            raise ValueError("PIN must contain only numeric digits.")

    @staticmethod
    def _hash(raw_pin: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}{raw_pin}".encode()).hexdigest()

    def __str__(self) -> str:
        return "Pin(****)"

    def __repr__(self) -> str:
        return "Pin(****)"