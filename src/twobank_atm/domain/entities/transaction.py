"""
Transaction entity — TWO Bank ATM.

EN: Immutable record of a single ATM operation.
ES: Registro inmutable de una operación en el cajero.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.money import Money


class TransactionType(Enum):
    """All possible ATM operation types."""
    WITHDRAWAL      = "withdrawal"
    DEPOSIT         = "deposit"
    BALANCE_INQUIRY = "balance_inquiry"
    PIN_CHANGE      = "pin_change"
    TRANSFER        = "transfer"


class TransactionStatus(Enum):
    """Outcome status of a transaction."""
    SUCCESS  = "success"
    FAILED   = "failed"
    REVERSED = "reversed"


@dataclass(frozen=True)
class Transaction:
    """
    Immutable entity representing a completed ATM operation.

    Attributes:
        id:               Unique transaction identifier (UUID).
        account_id:       UUID of the account involved.
        transaction_type: Type of operation performed.
        amount:           Money amount involved (None for inquiries).
        status:           Outcome of the transaction.
        timestamp:        When the transaction occurred.
        atm_id:           UUID of the ATM that processed it.
        note:             Optional description or error message.
    """

    account_id:       UUID
    transaction_type: TransactionType
    status:           TransactionStatus
    atm_id:           UUID
    id:               UUID            = field(default_factory=uuid4)
    amount:           Money | None    = field(default=None)
    timestamp:        datetime        = field(default_factory=lambda: datetime.now(timezone.utc))
    note:             str             = field(default="")

    # ──────────────────────────────────────────────
    # Factories
    # ──────────────────────────────────────────────
    @classmethod
    def record_withdrawal(
        cls,
        account_id: UUID,
        amount: Money,
        atm_id: UUID,
    ) -> "Transaction":
        """Record a successful cash withdrawal."""
        return cls(
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.SUCCESS,
            amount=amount,
            atm_id=atm_id,
            note=f"Cash withdrawal of {amount}",
        )

    @classmethod
    def record_deposit(
        cls,
        account_id: UUID,
        amount: Money,
        atm_id: UUID,
    ) -> "Transaction":
        """Record a successful cash deposit."""
        return cls(
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.SUCCESS,
            amount=amount,
            atm_id=atm_id,
            note=f"Cash deposit of {amount}",
        )

    @classmethod
    def record_balance_inquiry(
        cls,
        account_id: UUID,
        atm_id: UUID,
    ) -> "Transaction":
        """Record a balance inquiry (no amount involved)."""
        return cls(
            account_id=account_id,
            transaction_type=TransactionType.BALANCE_INQUIRY,
            status=TransactionStatus.SUCCESS,
            atm_id=atm_id,
            note="Balance inquiry",
        )

    @classmethod
    def record_failed(
        cls,
        account_id: UUID,
        transaction_type: TransactionType,
        atm_id: UUID,
        reason: str,
        amount: Money | None = None,
    ) -> "Transaction":
        """Record any failed operation with a reason."""
        return cls(
            account_id=account_id,
            transaction_type=transaction_type,
            status=TransactionStatus.FAILED,
            amount=amount,
            atm_id=atm_id,
            note=reason,
        )

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────
    def is_successful(self) -> bool:
        return self.status == TransactionStatus.SUCCESS

    def is_debit(self) -> bool:
        """Returns True if the operation reduced the account balance."""
        return self.transaction_type in (
            TransactionType.WITHDRAWAL,
            TransactionType.TRANSFER,
        )

    def is_credit(self) -> bool:
        """Returns True if the operation increased the account balance."""
        return self.transaction_type == TransactionType.DEPOSIT

    # ──────────────────────────────────────────────
    # Mini statement line
    # ──────────────────────────────────────────────
    def to_statement_line(self) -> str:
        """
        Format this transaction as a single receipt line.

        Example:
            2026-04-14 14:32  WITHDRAWAL   -€200.00  success
        """
        direction = ""
        if self.amount:
            direction = f"-{self.amount}" if self.is_debit() else f"+{self.amount}"

        return (
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M')}  "
            f"{self.transaction_type.value.upper():<18}"
            f"{direction:<14}"
            f"{self.status.value}"
        )

    # ──────────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────────
    def __str__(self) -> str:
        return self.to_statement_line()

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id!r}, "
            f"type={self.transaction_type.value!r}, "
            f"status={self.status.value!r}, "
            f"amount={self.amount!r})"
        )