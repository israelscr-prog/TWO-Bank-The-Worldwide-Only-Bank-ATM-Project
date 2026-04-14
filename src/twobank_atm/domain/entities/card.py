"""
Card entity — TWO Bank ATM.

EN: Represents a bank card linked to an account, with PIN and expiry logic.
ES: Representa una tarjeta bancaria vinculada a una cuenta, con PIN y expiración.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.pin import Pin
from twobank_atm.domain.exceptions.domain_exceptions import (
    CardExpiredError,
    CardBlockedError,
    InvalidPinError,
    PinBlockedError,
)


_MAX_PIN_ATTEMPTS = 3


class CardStatus(Enum):
    """Possible states of a bank card."""
    ACTIVE  = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"


@dataclass
class Card:
    """
    Entity representing a bank card.

    Attributes:
        id:              Unique card identifier (UUID).
        card_number:     Masked card number (e.g. '**** **** **** 1234').
        account_id:      UUID of the linked account.
        pin:             Hashed PIN value object.
        expiry_date:     Card expiration date.
        status:          Current card status.
        failed_attempts: Number of consecutive failed PIN attempts.
    """

    card_number:     str
    account_id:      UUID
    pin:             Pin
    expiry_date:     date
    id:              UUID       = field(default_factory=uuid4)
    status:          CardStatus = field(default=CardStatus.ACTIVE)
    failed_attempts: int        = field(default=0)

    # ──────────────────────────────────────────────
    # Factory
    # ──────────────────────────────────────────────
    @classmethod
    def issue(
        cls,
        card_number: str,
        account_id: UUID,
        raw_pin: str,
        expiry_date: date,
    ) -> "Card":
        """
        Issue a new bank card.

        Args:
            card_number: Card number string (will be masked on storage).
            account_id:  UUID of the account this card belongs to.
            raw_pin:     4-digit PIN string — hashed immediately, never stored.
            expiry_date: Expiration date of the card.

        Returns:
            New Card instance with ACTIVE status.

        Raises:
            ValueError: If card_number is empty or expiry_date is in the past.
        """
        if not card_number or not card_number.strip():
            raise ValueError("card_number cannot be empty.")
        if expiry_date < date.today():
            raise ValueError("Cannot issue a card with a past expiry date.")

        return cls(
            card_number=cls._mask(card_number),
            account_id=account_id,
            pin=Pin.create(raw_pin),
            expiry_date=expiry_date,
        )

    # ──────────────────────────────────────────────
    # PIN verification
    # ──────────────────────────────────────────────
    def verify_pin(self, raw_pin: str) -> None:
        """
        Verify the entered PIN against the stored hashed PIN.

        Args:
            raw_pin: PIN entered by the user at the ATM.

        Raises:
            CardBlockedError: If the card is already blocked.
            CardExpiredError: If the card is expired.
            PinBlockedError:  If this attempt exceeds max allowed failures.
            InvalidPinError:  If the PIN is wrong (with attempts remaining).
        """
        self._assert_usable()

        if self.pin.verify(raw_pin):
            self.failed_attempts = 0  # reset on success
            return

        self.failed_attempts += 1

        if self.failed_attempts >= _MAX_PIN_ATTEMPTS:
            self.status = CardStatus.BLOCKED
            raise PinBlockedError()

        raise InvalidPinError(attempts_left=_MAX_PIN_ATTEMPTS - self.failed_attempts)

    def change_pin(self, old_raw_pin: str, new_raw_pin: str) -> None:
        """
        Change the card PIN after verifying the old one.

        Args:
            old_raw_pin: Current PIN for verification.
            new_raw_pin: New PIN to set.
        """
        self.verify_pin(old_raw_pin)
        self.pin = Pin.create(new_raw_pin)

    # ──────────────────────────────────────────────
    # Status management
    # ──────────────────────────────────────────────
    def block(self) -> None:
        """Manually block the card."""
        self.status = CardStatus.BLOCKED

    def unblock(self) -> None:
        """Unblock the card and reset failed attempts."""
        self.status = CardStatus.ACTIVE
        self.failed_attempts = 0

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────
    def is_expired(self) -> bool:
        return date.today() > self.expiry_date

    def is_active(self) -> bool:
        return self.status == CardStatus.ACTIVE and not self.is_expired()

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    def _assert_usable(self) -> None:
        if self.status == CardStatus.BLOCKED:
            raise CardBlockedError()
        if self.is_expired():
            self.status = CardStatus.EXPIRED
            raise CardExpiredError()

    @staticmethod
    def _mask(card_number: str) -> str:
        """Mask all but the last 4 digits: '**** **** **** 1234'."""
        digits = card_number.replace(" ", "").replace("-", "")
        return f"**** **** **** {digits[-4:]}"

    # ──────────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────────
    def __str__(self) -> str:
        return (
            f"Card({self.card_number}) | "
            f"Expires: {self.expiry_date} | "
            f"Status: {self.status.value}"
        )

    def __repr__(self) -> str:
        return f"Card(id={self.id!r}, card_number={self.card_number!r}, status={self.status!r})"
    