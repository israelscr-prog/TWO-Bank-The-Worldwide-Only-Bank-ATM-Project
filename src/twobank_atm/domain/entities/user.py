"""
User entity — TWO Bank ATM.

EN: Represents a TWO Bank customer with personal data and linked cards.
ES: Representa un cliente del TWO Bank con datos personales y tarjetas vinculadas.

Author: TWO Bank Dev Team
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from twobank_atm.domain.exceptions.domain_exceptions import (
    AccountNotFoundError,
    CardNotFoundError,
)


class UserStatus(Enum):
    """Possible states of a user account."""
    ACTIVE   = "active"
    INACTIVE = "inactive"
    BANNED   = "banned"


@dataclass
class User:
    """
    Entity representing a TWO Bank customer.

    Attributes:
        id:         Unique user identifier (UUID).
        first_name: Customer's first name.
        last_name:  Customer's last name.
        email:      Customer's email address.
        national_id: National ID or passport number.
        status:     Current user status.
        card_ids:   List of UUIDs of cards linked to this user.
        account_ids: List of UUIDs of accounts owned by this user.
        created_at: Timestamp of user registration.
    """

    first_name:  str
    last_name:   str
    email:       str
    national_id: str
    id:          UUID       = field(default_factory=uuid4)
    status:      UserStatus = field(default=UserStatus.ACTIVE)
    card_ids:    list[UUID] = field(default_factory=list)
    account_ids: 