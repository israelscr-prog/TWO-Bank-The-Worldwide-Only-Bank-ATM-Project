# TWO Bank ATM — Domain Layer & First Test Suite

> **The Worldwide One Bank** | Development Log — Session 1  
> Language: **[English 🇬🇧]** · [Español 🇪🇸 → DOMAIN_LAYER_AND_TESTS.es.md]  
> Date: 15 April 2026 · Python 3.14 · pytest 9.0.3

---

## Session Summary

In this session, the complete **domain layer** of the TWO Bank ATM project was built from scratch using Clean Architecture principles. The session concluded with **68 unit tests passing** with a 100% success rate. This document records every component built, every decision made, and every issue encountered and resolved.

---

## What Was Built

### Value Objects

#### `Money` — `src/twobank_atm/domain/value_objects/money.py`

Represents an exact monetary amount with its associated currency. The central design constraint is financial precision: all amounts use `decimal.Decimal` rather than `float` to avoid binary floating-point representation errors (e.g., `0.1 + 0.2 != 0.3` in standard float arithmetic).

- Factory method `Money.of(amount, currency)` accepts `int`, `float`, `str`, or `Decimal`
- All amounts quantized to 2 decimal places using `ROUND_HALF_UP`
- Supports `+`, `-`, `*` operators with currency mismatch protection
- Supports `>`, `<`, `>=`, `<=`, `==` comparisons
- Raises `InvalidAmountError` for negative values and unparseable strings
- Raises `CurrencyMismatchError` when operating on different currencies
- Immutable: implemented as a `@dataclass(frozen=True)`

#### `Currency` — `src/twobank_atm/domain/value_objects/currency.py`

Represents an ISO 4217 currency with code, symbol, and name. The code is normalized to uppercase on construction so `"eur"` and `"EUR"` produce identical objects.

#### `Currencies` — `src/twobank_atm/domain/value_objects/currencies.py`

A static catalog of the six supported currencies: EUR, USD, GBP, JPY, CHF, and BTC (Bitcoin). Provides a `from_code(code: str) -> Currency` class method that raises `ValueError` for unsupported codes.

#### `Pin` — `src/twobank_atm/domain/value_objects/pin.py`

Represents a hashed bank card PIN. The raw PIN digit string is **never stored** — only its SHA-256 hash and the associated salt are retained.

Security implementation:
- Validates that the PIN is exactly 4 digits (numeric only)
- Generates a unique `secrets.token_hex(16)` salt per instance
- Hashes with `hashlib.sha256(salt + raw_pin)`
- Verifies with `secrets.compare_digest` to prevent timing attacks
- `__repr__` returns `"Pin(****)"` — the raw value never appears in logs or stack traces

---

### Entities

#### `Account` — `src/twobank_atm/domain/entities/account.py`

Represents a bank account. Enforces business rules at the entity level:

- An account cannot be opened with an empty owner name
- `deposit(money)` raises `AccountBlockedError` if the account is blocked and `InvalidAmountError` if the amount is zero or negative
- `withdraw(money)` raises `InsufficientFundsError` if the balance would go below zero
- Balance is stored as a `Money` value object — never a raw number
- Status transitions: `ACTIVE` → `BLOCKED` → `ACTIVE` (reversible), `ACTIVE` → `CLOSED` (irreversible)

#### `Card` — `src/twobank_atm/domain/entities/card.py`

Represents a bank card linked to an account by UUID. Key behaviours:

- `Card.issue()` factory method rejects empty card numbers and past expiry dates
- The card number is masked on storage: only the last 4 digits are visible (`****1234`)
- `verify_pin(raw_pin)` raises `CardBlockedError`, `CardExpiredError`, or `InvalidPinError`
- Three consecutive wrong PIN attempts automatically trigger `CardBlockedError`
- A correct PIN resets the failed attempt counter to zero

#### `User` — `src/twobank_atm/domain/entities/user.py`

Represents a bank customer. Stores `card_ids: list[UUID]` and `account_ids: list[UUID]` — references only, never the objects themselves. Name and email are normalized (stripped, lowercase for email) on creation.

#### `Transaction` — `src/twobank_atm/domain/entities/transaction.py`

An immutable, frozen record of a single ATM operation. Transaction types include: `WITHDRAWAL`, `DEPOSIT`, `BALANCE_INQUIRY`, `PIN_CHANGE`, `CARD_BLOCK`, `CARD_UNBLOCK`, `TRANSFER`, and `REVERSAL`.

Because the dataclass is `frozen=True`, no field can be modified after creation. To reverse a transaction, a new `REVERSAL` transaction is created — the original is never altered.

#### `ATMMachine` — `src/twobank_atm/domain/entities/atm_machine.py`

Represents the physical ATM hardware. Key responsibilities:

- Maintains a `cash_inventory: dict[int, int]` mapping denomination → count
- `dispense_cash(amount, currency)` uses a greedy largest-denomination-first algorithm
- Computes `total_cash` as the sum of all inventory values
- Transitions to `OUT_OF_CASH` status automatically when inventory reaches zero
- `load_cash(inventory)` restores inventory and transitions back to `ACTIVE`
- `put_in_maintenance()` / `restore_from_maintenance()` for servicing

---

### Domain Exceptions — `src/twobank_atm/domain/exceptions/domain_exceptions.py`

All exceptions inherit from `TWOBankError(Exception)`. The full hierarchy:

```
TWOBankError
├── InsufficientFundsError
├── AccountNotFoundError
├── AccountBlockedError
├── CardNotFoundError
├── CardExpiredError
├── CardBlockedError
├── InvalidPinError
├── PinBlockedError
├── ATMInsufficientCashError
├── InvalidAmountError
└── CurrencyMismatchError
```

---

## Test Suite Results

All 68 domain unit tests pass. Run time: **~0.2 seconds**.

```
pytest tests/unit/domain/ -v

platform win32 -- Python 3.14.4, pytest-9.0.3
collected 68 items

68 passed in 0.18s  ✅
```

### Test Coverage by File

| Test File | Class Under Test | Tests | All Pass |
|---|---|---|---|
| `test_money.py` | `Money` | 15 | ✅ |
| `test_currency.py` | `Currency` + `Currencies` | 10 | ✅ |
| `test_pin.py` | `Pin` | 8 | ✅ |
| `test_account.py` | `Account` | 12 | ✅ |
| `test_card.py` | `Card` | 9 | ✅ |
| `test_atm_machine.py` | `ATMMachine` | 10 | ✅ |
| `test_user.py` | `User` | 4 | ✅ |
| **Total** | | **68** | **✅ 100%** |

### Selected Test Cases

#### Money arithmetic precision
```python
def test_add(self):
    m1 = Money.of("10.50", EUR)
    m2 = Money.of("5.25", EUR)
    assert m1 + m2 == Money.of("15.75", EUR)

def test_subtract_negative_raises(self):
    m1 = Money.of("5.00", EUR)
    m2 = Money.of("10.00", EUR)
    with pytest.raises(InvalidAmountError):
        m1 - m2
```

#### Card lockout after 3 failed attempts
```python
def test_three_failures_block_card(self):
    card = make_card()
    for _ in range(3):
        with pytest.raises(InvalidPinError):
            card.verify_pin("9999")
    with pytest.raises(CardBlockedError):
        card.verify_pin("1234")
```

#### ATM greedy dispensing algorithm
```python
def test_dispense_exact_amount(self):
    atm = make_atm()   # inventory: {50:10, 20:20, 10:30}
    result = atm.dispense_cash(Money.of(170, EUR))
    assert result == {50: 3, 20: 1}
```

---

## Issues Encountered and Resolved

### Issue 1 — `ModuleNotFoundError: No module named 'src'`

**Symptom:** pytest collected 0 items due to import failures in all test files.  
**Cause:** pytest did not have the project root on `sys.path`.  
**Fix:** Added `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `pyproject.toml`.  
**Result:** pytest resolved the project root but still could not find `src.domain`.

### Issue 2 — `ModuleNotFoundError: No module named 'src.domain'`

**Symptom:** After Fix 1, pytest found `src` but not `src.domain`.  
**Cause:** The actual package structure is `src/twobank_atm/domain/`, not `src/domain/`. All imports used the wrong path prefix.  
**Fix 1:** Changed `pythonpath` from `["."]` to `["src"]` in `pyproject.toml`.  
**Fix 2:** Used VS Code's Find & Replace All (`Ctrl+Shift+H`) to replace all `from src.domain` → `from twobank_atm.domain` across the entire codebase.  
**Result:** All 6 test files collected and 67/68 tests passed on the first run.

### Issue 3 — `test_expired_card_raises` — `ValueError` on card creation

**Symptom:** 1 test failed with `ValueError: Cannot issue a card with a past expiry date.`  
**Cause:** The test tried to create a card directly with `expiry=date(2020, 1, 1)`, but `Card.issue()` correctly rejects past expiry dates at creation time.  
**Fix:** Changed the test to create a valid card first, then manually set `card.expiry_date = date(2020, 1, 1)` on the instance before calling `verify_pin()`.  
**Result:** All 68 tests passing.

### Issue 4 — `IndentationError` in `test_card.py`

**Symptom:** pytest failed to collect `test_card.py` with `IndentationError: expected an indented block after function definition on line 69`.  
**Cause:** During the fix for Issue 3, the method body was pasted without the required 4-space indentation, leaving an empty function definition.  
**Fix:** Rewrote the complete method with correct indentation.  
**Result:** All 68 tests passing. ✅

### Issue 5 — `DeprecationWarning: datetime.utcnow() is deprecated`

**Symptom:** 11 deprecation warnings appeared after all tests passed.  
**Cause:** `datetime.utcnow()` was removed in Python 3.12. Code used it in `default_factory` fields.  
**Fix:** Replaced all occurrences with `lambda: datetime.now(timezone.utc)` and added `timezone` to the relevant imports.  
**Result:** 0 warnings on subsequent runs.

---

## How to Run the Tests

```powershell
# Activate the virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Run all domain unit tests with verbose output
pytest tests/unit/domain/ -v

# Run with coverage report
pytest tests/unit/domain/ -v --cov=src/twobank_atm/domain --cov-report=term-missing

# Run a single test file
pytest tests/unit/domain/test_money.py -v

# Run a single test by name
pytest tests/unit/domain/test_card.py::TestPinVerification::test_three_failures_block_card -v
```

---

## Environment

| Component | Version |
|---|---|
| Python | 3.14.4 |
| pytest | 9.0.3 |
| pytest-cov | 7.1.0 |
| pytest-mock | 3.15.1 |
| pluggy | 1.6.0 |
| Platform | Windows 11 (win32) |

---

## Next Steps

The domain layer is complete and fully tested. The following layers are pending implementation in order:

1. **Application layer** (`src/twobank_atm/application/`) — use cases: `WithdrawCashUseCase`, `CheckBalanceUseCase`, `ChangePinUseCase`, `DepositCashUseCase`
2. **Infrastructure layer** (`src/twobank_atm/infrastructure/`) — in-memory repositories implementing the application-layer interfaces
3. **Presentation layer** (`src/twobank_atm/presentation/`) — CLI menu with ATM session flow
4. **Integration tests** — testing use cases with real infrastructure adapters
5. **End-to-end tests** — full ATM session simulation

