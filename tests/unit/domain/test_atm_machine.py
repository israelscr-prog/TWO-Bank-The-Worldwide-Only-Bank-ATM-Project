"""Tests for ATMMachine entity."""
import pytest
from twobank_atm.domain.entities.atm_machine import ATMMachine, ATMStatus
from twobank_atm.domain.value_objects.money import Money
from twobank_atm.domain.value_objects.currencies import Currencies
from twobank_atm.domain.exceptions.domain_exceptions import ATMInsufficientCashError

EUR = Currencies.EUR


def make_atm(initial_cash: dict[int, int] | None = None, location: str = "Gijón - Calle Corrida 12") -> ATMMachine:
    return ATMMachine.install(
        location=location,
        currency=EUR,
        initial_cash=initial_cash,
    )


class TestATMCreation:
    def test_install_atm(self):
        atm = make_atm()
        assert atm.is_operational()
        assert atm.location == "Gijón - Calle Corrida 12"

    def test_empty_location_raises(self):
        with pytest.raises(ValueError):
            ATMMachine.install(location="", currency=EUR)

    def test_total_cash(self):
        atm = make_atm({50: 2, 20: 2, 10: 2})
        # 100 + 40 + 20 = 160
        assert atm.total_cash() == Money.of("160", EUR)


class TestCashDispensing:
    def test_dispense_exact_amount(self):
        atm = make_atm({50: 10, 20: 10})
        result = atm.dispense_cash(Money.of("170", EUR))
        assert result == {50: 3, 20: 1}

    def test_dispense_reduces_inventory(self):
        atm = make_atm({50: 10})
        atm.dispense_cash(Money.of("100", EUR))
        assert atm.cash_inventory[50] == 8

    def test_dispense_zero_raises(self):
        atm = make_atm()
        with pytest.raises(Exception):
            atm.dispense_cash(Money.of("0", EUR))

    def test_dispense_more_than_available_raises(self):
        atm = make_atm({10: 1})  # only €10 available
        with pytest.raises(ATMInsufficientCashError):
            atm.dispense_cash(Money.of("500", EUR))

    def test_atm_flags_out_of_cash(self):
        atm = make_atm({10: 1})
        atm.dispense_cash(Money.of("10", EUR))
        assert atm.status == ATMStatus.OUT_OF_CASH


class TestATMStatus:
    def test_session_lifecycle(self):
        atm = make_atm()
        atm.start_session()
        assert atm.status == ATMStatus.IN_SESSION
        atm.end_session()
        assert atm.status == ATMStatus.IDLE

    def test_maintenance_blocks_operations(self):
        atm = make_atm()
        atm.set_maintenance()
        with pytest.raises(ATMInsufficientCashError):
            atm.dispense_cash(Money.of("50", EUR))

    def test_load_cash_restores_out_of_cash(self):
        atm = make_atm({10: 1})
        atm.dispense_cash(Money.of("10", EUR))
        assert atm.status == ATMStatus.OUT_OF_CASH
        atm.load_cash(50, 10)
        assert atm.status == ATMStatus.IDLE