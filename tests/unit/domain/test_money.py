"""Tests for Money value object."""
import pytest
from decimal import Decimal
from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies


EUR = Currencies.EUR
USD = Currencies.USD


class TestMoneyCreation:
    def test_create_with_factory(self):
        m = Money.of("50.00", EUR)
        assert m.amount == Decimal("50.00")
        assert m.currency == EUR

    def test_create_from_int(self):
        m = Money.of(100, EUR)
        assert m.amount == Decimal("100.00")

    def test_create_from_float(self):
        m = Money.of(9.99, EUR)
        assert m.amount == Decimal("9.99")

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError):
            Money.of("-10", EUR)

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            Money.of("abc", EUR)

    def test_is_immutable(self):
        m = Money.of("50", EUR)
        with pytest.raises(Exception):
            m.amount = Decimal("100")


class TestMoneyArithmetic:
    def test_add(self):
        result = Money.of("30", EUR).add(Money.of("20", EUR))
        assert result.amount == Decimal("50.00")

    def test_subtract(self):
        result = Money.of("50", EUR).subtract(Money.of("20", EUR))
        assert result.amount == Decimal("30.00")

    def test_subtract_to_zero(self):
        result = Money.of("50", EUR).subtract(Money.of("50", EUR))
        assert result.is_zero()

    def test_subtract_negative_raises(self):
        with pytest.raises(ValueError):
            Money.of("10", EUR).subtract(Money.of("50", EUR))

    def test_multiply(self):
        result = Money.of("20", EUR).multiply(3)
        assert result.amount == Decimal("60.00")

    def test_currency_mismatch_raises(self):
        with pytest.raises(ValueError):
            Money.of("50", EUR).add(Money.of("50", USD))


class TestMoneyComparison:
    def test_greater_than(self):
        assert Money.of("100", EUR).is_greater_than(Money.of("50", EUR))

    def test_less_than(self):
        assert Money.of("10", EUR).is_less_than(Money.of("50", EUR))

    def test_is_zero(self):
        assert Money.of("0", EUR).is_zero()

    def test_not_zero(self):
        assert not Money.of("1", EUR).is_zero()


class TestMoneyDisplay:
    def test_str_format(self):
        assert str(Money.of("1234.50", EUR)) == "€1,234.50"
