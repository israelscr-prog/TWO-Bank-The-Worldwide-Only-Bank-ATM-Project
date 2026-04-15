from dataclasses import dataclass
from uuid import UUID

from twobank_atm.application.ports.repositories.card_repository import CardRepository
from twobank_atm.application.ports.repositories.user_repository import UserRepository
from twobank_atm.application.ports.repositories.account_repository import AccountRepository


@dataclass
class AuthenticateUserRequest:
    card_id: UUID
    pin: str


@dataclass
class AuthenticateUserResponse:
    user_id: UUID
    primary_account_id: UUID


class AuthenticateUserUseCase:
    """
    Authenticates a user by card + PIN and returns the user and a primary account.

    The presentation layer can call this first to establish an authenticated session.
    """

    def __init__(
        self,
        card_repo: CardRepository,
        user_repo: UserRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._card_repo = card_repo
        self._user_repo = user_repo
        self._account_repo = account_repo

    def execute(self, request: AuthenticateUserRequest) -> AuthenticateUserResponse:
        # 1. Load card and verify PIN (domain will raise if invalid/blocked/expired)
        card = self._card_repo.get_by_id(request.card_id)
        card.verify_pin(request.pin)
        self._card_repo.save(card)

        # 2. Load user (assuming card has a user_id or we find user by account/card)
        # Aquí asumimos que User tiene la cuenta de la tarjeta en account_ids.
        # Dependiendo de tu modelo, esto se puede ajustar.
        user = self._user_repo.get_by_id(card.user_id)  # si Card tiene user_id

        # 3. Determine a primary account for the session
        if not user.account_ids:
            raise ValueError("Authenticated user has no linked accounts.")

        primary_account_id = user.account_ids[0]
        # Opcional: asegurar que la cuenta existe
        self._account_repo.get_by_id(primary_account_id)

        return AuthenticateUserResponse(
            user_id=user.id,
            primary_account_id=primary_account_id,
        )