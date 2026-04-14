"""Tests for Pin value object."""
import pytest
from twobank_atm.domain.value_objects.pin import Pin


class TestPinCreation:
    def test_create_valid_pin(self):
        pin = Pin.create("1234")
        assert pin is not None

    def test_pin_not_stored_in_repr(self):
        pin = Pin.create("1234")
        assert "1234" not in repr(pin)
        assert "****" in repr(pin)

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            Pin.create("123")

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            Pin.create("12345")

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError):
            Pin.create("ab12")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Pin.create("")


class TestPinVerification:
    def test_correct_pin_returns_true(self):
        pin = Pin.create("1234")
        assert pin.verify("1234") is True

    def test_wrong_pin_returns_false(self):
        pin = Pin.create("1234")
        assert pin.verify("0000") is False

    def test_different_pins_have_different_hashes(self):
        pin1 = Pin.create("1234")
        pin2 = Pin.create("1234")
        # Same PIN but different salts → different hashes
        assert pin1._hashed_pin != pin2._hashed_pin