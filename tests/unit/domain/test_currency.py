"""Tests for Currency value object and Currencies catalog."""
import pytest
from twobank_atm.domain.value_objects.currency import Currency
from twobank_atm.domain.value_objects.currencies import Currencies


class TestCurrency:
    def test_create_currency(self):
        c = Currency(code="EUR", symbol="€", name="Euro")
        assert c.code == "EUR"

    def test_code_normalized_to_uppercase(self):
        c = Currency(code="eur", symbol="€", name="Euro")
        assert c.code == "EUR"

    def test_empty_code_raises(self):
        with pytest.raises(ValueError):
            Currency(code="", symbol="€", name="Euro")

    def test_is_immutable(self):
        c = Currency(code="EUR", symbol="€", name="Euro")
        with pytest.raises(Exception):
            c.code = "USD"

    def test_equality(self):
        assert Currencies.EUR == Currencies.EUR
        assert Currencies.EUR != Currencies.USD


class TestCurrencies:
    def test_from_code_uppercase(self):
        assert Currencies.from_code("EUR") == Currencies.EUR

    def test_from_code_lowercase(self):
        assert Currencies.from_code("usd") == Currencies.USD

    def test_from_code_invalid_raises(self):
        with pytest.raises(ValueError):
            Currencies.from_code("XYZ")

    def test_all_contains_six_currencies(self):
        assert len(Currencies.ALL) == 6

    def test_bitcoin_in_catalog(self):
        assert Currencies.BTC in Currencies.ALL
        