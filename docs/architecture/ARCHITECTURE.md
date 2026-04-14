# TWO Bank ATM — Architecture Document

> **The Worldwide One Bank** | Architecture Reference v1.0.0  
> Language: **[English 🇬🇧]** · [Español 🇪🇸 → ARCHITECTURE.es.md]  
> Last updated: April 2026 · Python 3.14 · Clean Architecture

---

## Overview

TWO Bank ATM is a Python-based Automated Teller Machine simulation built following **Clean Architecture** principles, as defined by Robert C. Martin. The system is structured in four concentric layers where each layer depends only on the layer directly inside it — never outward. This rule, known as the **Dependency Rule**, ensures that business logic is completely isolated from frameworks, databases, and delivery mechanisms.

The primary goal of this architecture is long-term maintainability: the core banking rules can be tested, understood, and modified independently of any technical infrastructure decision.

---

## The Four Layers

```
┌─────────────────────────────────────────────────────┐
│              PRESENTATION (Layer 4)                 │
│         CLI · UI · API · Entry Points               │
├─────────────────────────────────────────────────────┤
│            INFRASTRUCTURE (Layer 3)                 │
│      Database · File System · External APIs         │
├─────────────────────────────────────────────────────┤
│             APPLICATION (Layer 2)                   │
│          Use Cases · Services · DTOs                │
├─────────────────────────────────────────────────────┤
│               DOMAIN (Layer 1)                      │
│    Entities · Value Objects · Domain Rules          │
└─────────────────────────────────────────────────────┘

         Dependency direction: INWARD ONLY →
```

### Layer 1 — Domain

The innermost layer. Contains all business rules, entities, value objects, and domain exceptions. This layer has **zero dependencies** on any external library or framework — it is pure Python. Changes to the database, the CLI, or any external service cannot affect this layer.

### Layer 2 — Application

Contains use cases — each representing a single user action (e.g., `WithdrawCashUseCase`, `CheckBalanceUseCase`). Use cases orchestrate domain objects and define the interfaces (repository protocols) that the infrastructure layer must implement.

### Layer 3 — Infrastructure

Implements the interfaces defined in the application layer. Contains the actual database adapters, file system access, external currency API clients, and any other I/O-bound code.

### Layer 4 — Presentation

The outermost layer. Contains the CLI menu, user input handling, and output formatting. This layer calls use cases and never interacts with the domain directly.

---

## Domain Layer Architecture

The domain layer is the heart of the system. It is divided into three categories of objects.

### Value Objects

Immutable objects identified solely by their value. Two instances with the same data are considered equal and interchangeable.

| Class | File | Responsibility |
|---|---|---|
| `Money` | `value_objects/money.py` | Represents an exact monetary amount with its currency. Uses `Decimal` for precision. Supports arithmetic and comparison. |
| `Currency` | `value_objects/currency.py` | Represents an ISO 4217 currency (code, symbol, name). Normalized to uppercase on creation. |
| `Currencies` | `value_objects/currencies.py` | Catalog of all supported currencies: EUR, USD, GBP, JPY, CHF, BTC. Provides `from_code()` lookup. |
| `Pin` | `value_objects/pin.py` | Stores a hashed + salted PIN. The raw value is never retained. Provides `verify()` for safe comparison. |

**Key design decision — `Decimal` over `float`:** Floating-point arithmetic cannot represent certain decimal values exactly. In banking, even a rounding error of `0.0000001` is unacceptable. All monetary amounts use `decimal.Decimal` with `ROUND_HALF_UP` quantization to 2 decimal places.

**Key design decision — PIN security:**
- `hashlib.sha256` hashes the PIN with a cryptographic salt
- `secrets.token_hex(16)` generates a unique salt per PIN instance, defeating rainbow table attacks
- `secrets.compare_digest` compares hashes in constant time, preventing timing attacks

### Entities

Mutable objects identified by a unique ID rather than their data. Two accounts with the same balance are still different accounts.

| Class | File | Responsibility |
|---|---|---|
| `Account` | `entities/account.py` | Bank account with balance, currency, and status. Enforces business rules for deposit and withdrawal. |
| `Card` | `entities/card.py` | Bank card linked to an account. Manages PIN verification with lockout after 3 failed attempts. |
| `User` | `entities/user.py` | Bank customer. Holds references (UUIDs) to their cards and accounts. Normalizes name and email on creation. |
| `Transaction` | `entities/transaction.py` | Immutable record of a single ATM operation. Frozen after creation — records are permanent. |
| `ATMMachine` | `entities/atm_machine.py` | Physical ATM. Manages cash inventory and dispenses bills using a greedy largest-denomination-first algorithm. |

**Key design decision — `User` stores IDs, not objects:** The domain layer never holds references to other live entities directly. `User.card_ids` is a `list[UUID]`, not a `list[Card]`. This keeps the domain free of repository dependencies and prevents deep object graphs from forming.

**Key design decision — `Transaction` is frozen:** A `Transaction` uses `@dataclass(frozen=True)`, making it immutable like a value object. Financial records must never be modified after creation. To reverse an operation, a new `REVERSED` transaction is recorded rather than altering the original.

### Domain Exceptions

A hierarchy of custom exceptions representing business rule violations. All inherit from `TWOBankError`, which inherits from `Exception`.

```
Exception
└── TWOBankError
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

**Key design decision — custom exception hierarchy:** Using `TWOBankError` as the base allows the presentation layer to catch all banking errors with a single `except TWOBankError` while still allowing fine-grained handling at lower levels. It also prevents infrastructure exceptions (e.g., `sqlalchemy.exc.IntegrityError`) from leaking into the domain.

---

## ATM Cash Dispensing Algorithm

The `ATMMachine.dispense_cash()` method implements a greedy algorithm that dispenses cash using the **largest available denomination first**. This minimizes the number of notes dispensed and matches real-world ATM behavior.

**Example:** Request for €170 with inventory `{50: 10, 20: 20, 10: 30}`:

```
Step 1: 170 ÷ 50 = 3 notes  → remaining: 170 - 150 = 20
Step 2:  20 ÷ 20 = 1 note   → remaining:  20 -  20 =  0  ✓

Result: { 50: 3, 20: 1 }  →  3 × €50 + 1 × €20 = €170
```

The algorithm operates in three phases:
1. **Calculate** — determine the combination of notes without modifying inventory
2. **Validate** — if `remaining > 0` after all denominations, raise `ATMInsufficientCashError`
3. **Commit** — only deduct from inventory after validation passes

This three-phase approach ensures the ATM's inventory is never partially deducted on a failed dispense operation.

---

## ATM Session Lifecycle

```
    [IDLE] ──── card inserted ────→ [IN_SESSION]
      ↑                                   │
      └──────── card ejected ─────────────┘
      │
      ├── maintenance call ──→ [MAINTENANCE] ──── restore ──→ [IDLE]
      │
      └── last note dispensed ──→ [OUT_OF_CASH] ── load_cash ──→ [IDLE]
```

---

## Project Structure

```
TWO-Bank-The-Worldwide-Only-Bank-ATM-Project/
│
├── src/twobank_atm/
│   ├── domain/
│   │   ├── entities/          ← Account, Card, User, Transaction, ATMMachine
│   │   ├── value_objects/     ← Money, Currency, Currencies, Pin
│   │   └── exceptions/        ← domain_exceptions.py
│   │
│   ├── application/           ← Use cases (Layer 2) — to be implemented
│   ├── infrastructure/        ← DB adapters, APIs (Layer 3) — to be implemented
│   └── presentation/          ← CLI (Layer 4) — to be implemented
│
├── tests/
│   ├── unit/domain/           ← 68 domain tests — all passing ✅
│   ├── unit/application/      ← to be implemented
│   ├── integration/           ← to be implemented
│   └── e2e/                   ← to be implemented
│
├── docs/
│   └── architecture/          ← this document
│
├── pyproject.toml
├── main.py
└── README.md
```

---

## Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Language | Python 3.14 | Type hints, dataclasses, `match` statements |
| Money precision | `decimal.Decimal` | Exact arithmetic — no floating-point errors |
| Unique IDs | `uuid.UUID` / `uuid4()` | Standard, collision-resistant entity identifiers |
| PIN hashing | `hashlib.sha256` + `secrets` | Industry-standard cryptographic security |
| Data modeling | `@dataclass` / `frozen=True` | Concise, immutable value objects |
| Testing | `pytest` + `pytest-cov` | 68 domain unit tests — 100% pass rate |
| Type checking | `mypy` | Static analysis enforcing the Dependency Rule |
| CI/CD | GitHub Actions | Automated lint, type-check, test on every push |

---

## Architectural Decision Records

Full ADR documents are located in `docs/adr/`.

| ADR | Decision |
|---|---|
| ADR-001 | Clean Architecture chosen over layered (MVC) architecture |
| ADR-002 | `decimal.Decimal` over `float` for all monetary values |
| ADR-003 | UUID as primary key for all entities |
| ADR-004 | Bilingual documentation (English + Spanish) |

