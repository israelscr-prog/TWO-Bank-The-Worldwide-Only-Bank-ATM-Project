"""
ATMMachine entity — TWO Bank ATM.

EN: Manages physical cash inventory and ATM operational state.
ES: Gestiona el inventario físico de efectivo y el estado operacional del cajero.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currency import Currency
from twobank_atm.domain.exceptions.domain_exceptions import (
    ATMInsufficientCashError,
    InvalidAmountError,
)


class ATMStatus(Enum):
    """Possible operational states of the ATM."""
    IDLE         = "idle"           # waiting for a card
    IN_SESSION   = "in_session"     # card inserted, user operating
    MAINTENANCE  = "maintenance"    # out of service
    OUT_OF_CASH  = "out_of_cash"    # empty cassettes


# Standard EUR denominations — largest first for optimal dispensing
_DEFAULT_DENOMINATIONS = [500, 200, 100, 50, 20, 10, 5]


@dataclass
class ATMMachine:
    """
    Entity representing the physical ATM machine.

    Attributes:
        id:           Unique ATM identifier (UUID).
        location:     Human-readable location (e.g. 'Gijón - Calle Corrida 12').
        currency:     Base currency of the cash in this ATM.
        cash_inventory: Dict mapping denomination (int) → note count (int).
        status:       Current operational status.
    """

    location:       str
    currency:       Currency
    id:             UUID             = field(default_factory=uuid4)
    cash_inventory: dict[int, int]   = field(default_factory=dict)
    status:         ATMStatus        = field(default=ATMStatus.IDLE)

    # ──────────────────────────────────────────────
    # Factory
    # ──────────────────────────────────────────────
    @classmethod
    def install(
        cls,
        location: str,
        currency: Currency,
        initial_cash: dict[int, int] | None = None,
    ) -> "ATMMachine":
        """
        Install a new ATM at a given location.

        Args:
            location:     Physical location description.
            currency:     Currency of notes loaded in this ATM.
            initial_cash: Dict of {denomination: note_count}.
                          e.g. {50: 100, 20: 200, 10: 500}
                          Defaults to empty cassettes.

        Returns:
            New ATMMachine instance ready for operation.

        Raises:
            ValueError: If location is empty or denomination is invalid.
        """
        if not location or not location.strip():
            raise ValueError("location cannot be empty.")

        inventory = initial_cash or {}
        cls._validate_inventory(inventory)

        atm = cls(location=location.strip(), currency=currency)
        atm.cash_inventory = dict(inventory)
        return atm

    # ──────────────────────────────────────────────
    # Cash management
    # ──────────────────────────────────────────────
    def load_cash(self, denomination: int, count: int) -> None:
        """
        Load notes into a cassette (maintenance operation).

        Args:
            denomination: Bill value (e.g. 50, 20, 10).
            count:        Number of notes to add.
        """
        if denomination <= 0 or count <= 0:
            raise ValueError("denomination and count must be positive.")
        self.cash_inventory[denomination] = (
            self.cash_inventory.get(denomination, 0) + count
        )
        if self.status == ATMStatus.OUT_OF_CASH:
            self.status = ATMStatus.IDLE

    def dispense_cash(self, amount: Money) -> dict[int, int]:
        """
        Dispense cash using largest denominations first.

        Args:
            amount: Money to dispense — must match ATM currency.

        Returns:
            Dict of {denomination: notes_dispensed}.
            e.g. {50: 3, 20: 1} for €170

        Raises:
            InvalidAmountError:      If amount is zero, negative, or not divisible
                                     by the smallest available denomination.
            ATMInsufficientCashError: If ATM cannot cover the requested amount.
        """
        self._assert_operational()

        if amount.is_zero():
            raise InvalidAmountError("Amount must be greater than zero.")
        if amount.currency != self.currency:
            raise InvalidAmountError(
                f"ATM dispenses {self.currency.code}, not {amount.currency.code}."
            )

        remaining = int(amount.amount)
        dispensed: dict[int, int] = {}

        # Sort denominations largest → smallest
        for denomination in sorted(self.cash_inventory.keys(), reverse=True):
            if remaining <= 0:
                break
            available = self.cash_inventory[denomination]
            needed = min(remaining // denomination, available)
            if needed > 0:
                dispensed[denomination] = needed
                remaining -= needed * denomination

        if remaining > 0:
            raise ATMInsufficientCashError(requested=str(amount))

        # Commit — deduct from inventory
        for denomination, count in dispensed.items():
            self.cash_inventory[denomination] -= count

        # Auto-flag if now empty
        if self.total_cash().is_zero():
            self.status = ATMStatus.OUT_OF_CASH

        return dispensed

    # ──────────────────────────────────────────────
    # Session management
    # ──────────────────────────────────────────────
    def start_session(self) -> None:
        """Mark ATM as in-session when a card is inserted."""
        self._assert_operational()
        self.status = ATMStatus.IN_SESSION

    def end_session(self) -> None:
        """Return ATM to idle after card is ejected."""
        self.status = ATMStatus.IDLE

    def set_maintenance(self) -> None:
        """Take the ATM out of service."""
        self.status = ATMStatus.MAINTENANCE

    def restore(self) -> None:
        """Bring the ATM back into service after maintenance."""
        self.status = ATMStatus.IDLE

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────
    def total_cash(self) -> Money:
        """Calculate total cash value currently in the ATM."""
        total = sum(
            denom * count
            for denom, count in self.cash_inventory.items()
        )
        return Money.of(str(total), self.currency)

    def is_operational(self) -> bool:
        return self.status in (ATMStatus.IDLE, ATMStatus.IN_SESSION)

    def can_dispense(self, amount: Money) -> bool:
        """Check if ATM has enough cash without actually dispensing."""
        try:
            # Simulate dispensing without committing
            remaining = int(amount.amount)
            for denom in sorted(self.cash_inventory.keys(), reverse=True):
                if remaining <= 0:
                    break
                needed = min(remaining // denom, self.cash_inventory[denom])
                remaining -= needed * denom
            return remaining == 0
        except Exception:
            return False

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    def _assert_operational(self) -> None:
        if self.status == ATMStatus.MAINTENANCE:
            raise ATMInsufficientCashError("ATM is under maintenance.")
        if self.status == ATMStatus.OUT_OF_CASH:
            raise ATMInsufficientCashError("ATM is out of cash.")

    @staticmethod
    def _validate_inventory(inventory: dict[int, int]) -> None:
        for denom, count in inventory.items():
            if denom <= 0:
                raise ValueError(f"Invalid denomination: {denom}")
            if count < 0:
                raise ValueError(f"Note count cannot be negative: {count}")

    # ──────────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────────
    def __str__(self) -> str:
        return (
            f"ATM({self.id}) | "
            f"{self.location} | "
            f"Cash: {self.total_cash()} | "
            f"Status: {self.status.value}"
        )

    def __repr__(self) -> str:
        return (
            f"ATMMachine(id={self.id!r}, "
            f"location={self.location!r}, "
            f"status={self.status!r})"
        )