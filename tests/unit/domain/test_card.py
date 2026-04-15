"""Tests for Card entity."""
import pytest
from datetime import date
from uuid import uuid4
from twobank_atm.domain.entities import card
from twobank_atm.domain.entities.card import Card, CardStatus
from twobank_atm.domain.exceptions.domain_exceptions import (
    CardBlockedError,
    CardExpiredError,
    InvalidPinError,
    PinBlockedError,
)


def make_card(pin: str = "1234", expiry: date = date(2030, 12, 31)) -> Card:
    return Card.issue(
        card_number="4111111111111234",
        account_id=uuid4(),
        raw_pin=pin,
        expiry_date=expiry,
    )


class TestCardCreation:
    def test_card_number_is_masked(self):
        card = make_card()
        assert card.card_number == "**** **** **** 1234"

    def test_past_expiry_raises(self):
        with pytest.raises(ValueError):
            make_card(expiry=date(2020, 1, 1))

    def test_empty_card_number_raises(self):
        with pytest.raises(ValueError):
            Card.issue("", uuid4(), "1234", date(2030, 1, 1))


class TestPinVerification:
    def test_correct_pin_passes(self):
        card = make_card()
        card.verify_pin("1234")  # no exception = success

    def test_wrong_pin_raises(self):
        card = make_card()
        with pytest.raises(InvalidPinError):
            card.verify_pin("0000")

    def test_failed_attempts_increment(self):
        card = make_card()
        with pytest.raises(InvalidPinError):
            card.verify_pin("0000")
        assert card.failed_attempts == 1

    def test_three_failures_block_card(self):
        card = make_card()
        for _ in range(2):
            with pytest.raises(InvalidPinError):
                card.verify_pin("0000")
        with pytest.raises(PinBlockedError):
            card.verify_pin("0000")
        assert card.status == CardStatus.BLOCKED

    def test_correct_pin_resets_attempts(self):
        card = make_card()
        with pytest.raises(InvalidPinError):
            card.verify_pin("0000")
        card.verify_pin("1234")
        assert card.failed_attempts == 0

    def test_expired_card_raises(self):
        card = make_card()
        card.expiry_date = date(2020, 1, 1)
        with pytest.raises(CardExpiredError):
            card.verify_pin("1234")
            