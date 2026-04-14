<p align="right">
  <a href="./README.md">English</a> | <a href="./README.es.md">Español</a>
</p>

# 🏦 TWO Bank ATM
### The Worldwide One Bank

> A professional-grade ATM simulation built with Python 3.14, Clean Architecture,
> full bilingual support (English & Spanish), and an industry-standard CI/CD pipeline.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-orange)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Tests](https://img.shields.io/badge/Tests-Unit%20%7C%20Integration%20%7C%20E2E-purple)
![i18n](https://img.shields.io/badge/Languages-EN%20%7C%20ES-red)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Running Tests](#-running-tests)
- [Environment Variables](#-environment-variables)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## 🎯 About the Project

**TWO Bank ATM** is a fully-featured ATM software system designed and built
from scratch using professional software engineering principles. The project
demonstrates Clean Architecture, Domain-Driven Design patterns, SOLID principles,
full bilingual internationalisation, secure PIN handling, and a complete
CI/CD pipeline — all in Python 3.14.

This project is built progressively, layer by layer, following best practices
used in real-world banking software development.

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🔐 Authentication | 🔲 Planned | Card number + bcrypt-hashed PIN |
| 💶 Withdraw Cash | 🔲 Planned | Multi-denomination dispensing (€5/€10/€20/€50) |
| 💰 Deposit Cash | 🔲 Planned | Cash deposit with instant balance update |
| 📊 Check Balance | 🔲 Planned | Real-time available balance display |
| 🔄 Transfer Funds | 🔲 Planned | Account-to-account transfers |
| 📋 Mini Statement | 🔲 Planned | Last 10 transactions with receipt |
| 💱 Currency Converter | 🔲 Planned | Live rates: EUR → USD, GBP, JPY, CHF, BTC |
| 🔑 Change PIN | 🔲 Planned | Secure PIN change with confirmation |
| 🛡️ Admin Panel | 🔲 Planned | Create/block accounts, view inventory |
| 🌍 Bilingual UI | ✅ Ready | Full English & Spanish support |
| ⏱️ Session Timeout | 🔲 Planned | Auto-logout after 90 seconds inactivity |
| 🔒 Card Blocking | 🔲 Planned | Block after 3 consecutive PIN failures |

---

## 🏗️ Architecture

This project follows **Clean Architecture** — a 4-layer model where dependencies
only point **inward**. Business logic is completely isolated from databases,
APIs, and user interfaces.

```
┌─────────────────────────────────────────────────┐
│           LAYER 4 — PRESENTATION                │
│         CLI (Phase 1) · GUI (Phase 2)           │
├─────────────────────────────────────────────────┤
│           LAYER 3 — INFRASTRUCTURE              │
│       SQLite · bcrypt · ExchangeRate API        │
├─────────────────────────────────────────────────┤
│           LAYER 2 — APPLICATION                 │
│        Use Cases · Ports · DTOs                 │
├─────────────────────────────────────────────────┤
│           LAYER 1 — DOMAIN  ← innermost         │
│    Entities · Value Objects · Exceptions        │
│         Zero external dependencies              │
└─────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Database | SQLite | Zero server setup, real SQL, portable |
| PIN Security | bcrypt cost=12 | Industry standard, ~250ms/hash, brute-force resistant |
| Money handling | Integer cents | Zero floating-point arithmetic errors |
| i18n | JSON locale files | Human-readable, no compilation, easy to extend |
| Architecture | Clean Architecture | Testable, swappable layers, SOLID principles |

> 📖 Full rationale in [`docs/decisions/`](docs/decisions/)

---

## 📁 Project Structure

```
TWO-Bank-ATM/
│
├── 📄 main.py                        ← Single entry point
├── 📄 requirements.txt               ← All dependencies
├── 📄 pyproject.toml                 ← Project config & tool settings
├── 📄 .env.example                   ← Environment variable template
│
├── 📁 .github/workflows/             ← CI/CD pipeline (GitHub Actions)
├── 📁 .vscode/                       ← VS Code settings & debug configs
│
├── 📁 src/twobank_atm/
│   ├── 📁 domain/                    ← Layer 1: Pure business logic
│   │   ├── entities/                 ← Account, Card, User, Transaction, ATM
│   │   ├── value_objects/            ← Money, Currency, Pin (immutable)
│   │   └── exceptions/               ← All domain-specific errors
│   │
│   ├── 📁 application/               ← Layer 2: Use cases & contracts
│   │   ├── use_cases/                ← One file per ATM action
│   │   ├── ports/                    ← Abstract interfaces (repositories + services)
│   │   └── dtos/                     ← Data Transfer Objects
│   │
│   ├── 📁 infrastructure/            ← Layer 3: Technical implementations
│   │   ├── database/                 ← SQLite connection, migrations, repositories
│   │   ├── security/                 ← bcrypt PIN hashing, session management
│   │   ├── services/                 ← Exchange rate API, receipt generator
│   │   └── seeders/                  ← Test data (5 users + ATM inventory)
│   │
│   ├── 📁 presentation/              ← Layer 4: User interfaces
│   │   ├── cli/                      ← Terminal interface (Phase 1)
│   │   └── gui/                      ← Tkinter GUI (Phase 2 - reserved)
│   │
│   ├── 📁 i18n/                      ← Internationalisation engine
│   │   └── locales/en/ + es/         ← Translation files (EN ✅ ES ✅)
│   │
│   └── 📁 config/                    ← Settings & constants
│
├── 📁 tests/
│   ├── unit/                         ← Fast isolated tests (no DB, no API)
│   ├── integration/                  ← Tests with real DB and real services
│   └── e2e/                          ← Full user flow simulations
│
├── 📁 scripts/                       ← DB setup and seeding scripts
├── 📁 docs/                          ← Architecture docs, ADRs, guides
├── 📁 data/                          ← SQLite database (git-ignored)
└── 📁 logs/                          ← Runtime logs (git-ignored)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher (3.14 recommended)
- Git
- VS Code (recommended) with Python extension

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/TWO-Bank-The-Worldwide-Only-Bank-ATM-Project.git
cd TWO-Bank-The-Worldwide-Only-Bank-ATM-Project

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
# Open .env and fill in your values

# 5. Run the project
python main.py
```

### Expected output

```
=============================================
   TWO Bank ATM - The Worldwide One Bank
=============================================
  Status: Project structure OK
  Next:   Building Domain layer...
=============================================
```

---

## 🧪 Running Tests

```bash
# All tests
pytest

# Unit tests only (fast, no external dependencies)
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# End-to-end tests
pytest tests/e2e/ -v

# With coverage report
pytest --cov=src/twobank_atm --cov-report=term-missing
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `./data/twobank.db` | SQLite database file path |
| `BCRYPT_ROUNDS` | `12` | bcrypt hashing cost factor |
| `SESSION_TIMEOUT_SECONDS` | `90` | Idle session timeout |
| `MAX_PIN_ATTEMPTS` | `3` | Failed attempts before card block |
| `ATM_ID` | `ATM-001` | ATM machine identifier |
| `ATM_MAX_WITHDRAWAL_EUR` | `600` | Maximum single withdrawal |
| `ATM_DAILY_LIMIT_EUR` | `1200` | Daily withdrawal limit |
| `EXCHANGE_RATE_API_KEY` | — | Free key from exchangerate-api.com |
| `DEFAULT_LANGUAGE` | `en` | Default UI language (`en` or `es`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 🗺️ Roadmap

### Phase 1 — CLI (In Progress)
- [x] Project structure & Clean Architecture skeleton
- [x] Bilingual translation files (EN + ES)
- [x] GitHub Actions CI/CD pipeline
- [ ] Domain layer: Money, Account, Card, Transaction entities
- [ ] Application layer: All 10 use cases
- [ ] Infrastructure layer: SQLite, bcrypt, Exchange Rate API
- [ ] Presentation layer: All CLI screens
- [ ] Full test suite (unit + integration + e2e)

### Phase 2 — GUI (Planned)
- [ ] Tkinter graphical interface
- [ ] ATM-style button layout
- [ ] Card insert animation

---

## 🤝 Contributing

This is a learning project built step by step. All contributions welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow the code standards in [`docs/DOCUMENTATION_RULES.md`](docs/DOCUMENTATION_RULES.md)
4. Write tests for your code
5. Submit a Pull Request

> 📖 See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

---

## 👥 Team

| Role | Name |
|------|------|
| Lead Developer | TWO Bank Dev Team |
| Architecture | Clean Architecture (Uncle Bob) |
| Security | bcrypt + OWASP guidelines |

---

## 📄 License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ using Python 3.14 · Clean Architecture · Test-Driven Development</sub>
</div>
