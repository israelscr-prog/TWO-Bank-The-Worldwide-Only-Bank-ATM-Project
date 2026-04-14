# Contributing to TWO Bank ATM

Thank you for contributing to TWO Bank ATM — The Worldwide One Bank.
Please read these guidelines before submitting any code.

---

## 🌿 Branching Strategy

```
main          ← Production-ready code only. Protected.
develop       ← Integration branch. All features merge here first.
feature/*     ← New features. Branch from develop.
fix/*         ← Bug fixes. Branch from develop.
hotfix/*      ← Critical production fixes. Branch from main.
```

### Branch naming examples
```bash
git checkout -b feature/withdraw-cash-use-case
git checkout -b feature/money-value-object
git checkout -b fix/pin-validation-error
git checkout -b hotfix/session-timeout-crash
```

---

## 📝 Commit Message Format

Every commit message must follow this structure:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

### Types
| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Adding or fixing tests |
| `docs` | Documentation only |
| `refactor` | Code restructuring, no behaviour change |
| `style` | Formatting only (Black, Ruff) |
| `chore` | Build tools, dependencies, config |

### Examples
```
feat(domain): add Money value object with integer cent storage
fix(auth): correct PIN attempt counter reset on successful login
test(domain): add unit tests for Account balance validation
docs(readme): update installation instructions for Windows
refactor(withdrawal): extract denomination logic to ATMMachine entity
chore(deps): upgrade bcrypt to 4.2.0
```

---

## 🏗️ Code Standards

All code must follow the rules in [`docs/DOCUMENTATION_RULES.md`](docs/DOCUMENTATION_RULES.md).

### Quick checklist before every commit

- [ ] Every function has a docstring (description, Args, Returns, Raises)
- [ ] Every module has a module-level docstring (Module, Layer, Description, Author)
- [ ] Type hints on all function parameters and return values
- [ ] No magic numbers — use `constants.py`
- [ ] No hardcoded strings in UI — use `t.get("key")`
- [ ] All new code has unit tests
- [ ] `black src/ tests/` passes with no changes
- [ ] `ruff check src/ tests/` passes with no errors

---

## 🧪 Testing Requirements

Every new feature must include tests before a PR can be merged.

```bash
# Run before submitting a PR
pytest tests/unit/ -v          # Must all pass
pytest tests/integration/ -v   # Must all pass
pytest --cov=src/twobank_atm --cov-report=term-missing
# Coverage must not drop below 80%
```

### Test structure (GIVEN / WHEN / THEN)
```python
def test_withdrawal_reduces_balance():
    # GIVEN
    account = Account(balance=Money(10000, "EUR"))  # €100.00

    # WHEN
    account.debit(Money(3000, "EUR"))               # €30.00

    # THEN
    assert account.balance == Money(7000, "EUR")    # €70.00
```

---

## 🔄 Pull Request Process

1. Ensure all tests pass locally
2. Update documentation if behaviour changed
3. Fill in the PR template completely
4. Request review from at least one team member
5. Squash commits before merging to develop

---

## 🚫 What NOT to Do

- Never commit `.env` files or secrets
- Never hardcode EUR amounts as floats (`50.25`) — use integer cents (`5025`)
- Never add UI strings directly — use the translator
- Never skip the `__init__.py` in a new package folder
- Never break the dependency rule (outer layers cannot import inner layers)

---

## 🆘 Questions?

Open a GitHub Issue with the label `question`.
