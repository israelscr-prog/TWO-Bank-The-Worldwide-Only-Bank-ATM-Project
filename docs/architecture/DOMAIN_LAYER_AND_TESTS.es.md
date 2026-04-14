# TWO Bank ATM — Capa de Dominio y Primera Suite de Tests

> **The Worldwide One Bank** | Registro de Desarrollo — Sesión 1  
> Idioma: [English 🇬🇧 → DOMAIN_LAYER_AND_TESTS.md] · **[Español 🇪🇸]**  
> Fecha: 15 de Abril de 2026 · Python 3.14 · pytest 9.0.3

---

## Resumen de la Sesión

En esta sesión se construyó desde cero la **capa de dominio** completa del proyecto TWO Bank ATM aplicando principios de Clean Architecture. La sesión concluyó con **68 tests unitarios pasando** con un 100% de éxito. Este documento registra cada componente construido, cada decisión tomada y cada problema encontrado y resuelto.

---

## Qué Se Construyó

### Value Objects

#### `Money` — `src/twobank_atm/domain/value_objects/money.py`

Representa una cantidad monetaria exacta con su divisa asociada. La restricción de diseño central es la precisión financiera: todos los importes usan `decimal.Decimal` en lugar de `float` para evitar errores de representación en coma flotante binaria (p. ej., `0.1 + 0.2 != 0.3` en aritmética estándar de float).

- Método factory `Money.of(amount, currency)` acepta `int`, `float`, `str` o `Decimal`
- Todos los importes cuantizados a 2 decimales usando `ROUND_HALF_UP`
- Soporta operadores `+`, `-`, `*` con protección frente a divisas incompatibles
- Soporta comparaciones `>`, `<`, `>=`, `<=`, `==`
- Lanza `InvalidAmountError` para valores negativos y cadenas no parseables
- Lanza `CurrencyMismatchError` al operar con divisas distintas
- Inmutable: implementado como `@dataclass(frozen=True)`

#### `Currency` — `src/twobank_atm/domain/value_objects/currency.py`

Representa una divisa ISO 4217 con código, símbolo y nombre. El código se normaliza a mayúsculas en la construcción, de modo que `"eur"` y `"EUR"` producen objetos idénticos.

#### `Currencies` — `src/twobank_atm/domain/value_objects/currencies.py`

Un catálogo estático de las seis divisas soportadas: EUR, USD, GBP, JPY, CHF y BTC (Bitcoin). Proporciona el método de clase `from_code(code: str) -> Currency` que lanza `ValueError` para códigos no soportados.

#### `Pin` — `src/twobank_atm/domain/value_objects/pin.py`

Representa un PIN de tarjeta bancaria hasheado. La cadena de dígitos del PIN nunca se almacena — solo se retienen su hash SHA-256 y el salt asociado.

Implementación de seguridad:
- Valida que el PIN sea exactamente 4 dígitos (solo numérico)
- Genera un salt único `secrets.token_hex(16)` por instancia
- Hashea con `hashlib.sha256(salt + raw_pin)`
- Verifica con `secrets.compare_digest` para prevenir ataques de timing
- `__repr__` devuelve `"Pin(****)"` — el valor real nunca aparece en logs ni en trazas de pila

---

### Entidades

#### `Account` — `src/twobank_atm/domain/entities/account.py`

Representa una cuenta bancaria. Aplica las reglas de negocio a nivel de entidad:

- Una cuenta no puede abrirse con un nombre de titular vacío
- `deposit(money)` lanza `AccountBlockedError` si la cuenta está bloqueada e `InvalidAmountError` si el importe es cero o negativo
- `withdraw(money)` lanza `InsufficientFundsError` si el saldo resultante sería negativo
- El saldo se almacena como un value object `Money` — nunca como un número crudo
- Transiciones de estado: `ACTIVE` → `BLOCKED` → `ACTIVE` (reversible), `ACTIVE` → `CLOSED` (irreversible)

#### `Card` — `src/twobank_atm/domain/entities/card.py`

Representa una tarjeta bancaria vinculada a una cuenta por UUID. Comportamientos clave:

- El método factory `Card.issue()` rechaza números de tarjeta vacíos y fechas de caducidad pasadas
- El número de tarjeta se enmascara al almacenarse: solo son visibles los 4 últimos dígitos (`****1234`)
- `verify_pin(raw_pin)` lanza `CardBlockedError`, `CardExpiredError` o `InvalidPinError`
- Tres intentos de PIN incorrectos consecutivos activan automáticamente `CardBlockedError`
- Un PIN correcto reinicia el contador de intentos fallidos a cero

#### `User` — `src/twobank_atm/domain/entities/user.py`

Representa un cliente del banco. Almacena `card_ids: list[UUID]` y `account_ids: list[UUID]` — solo referencias, nunca los objetos en sí. El nombre y el email se normalizan (strip, minúsculas para email) al crearse.

#### `Transaction` — `src/twobank_atm/domain/entities/transaction.py`

Un registro inmutable y congelado de una única operación en el cajero. Los tipos de transacción incluyen: `WITHDRAWAL`, `DEPOSIT`, `BALANCE_INQUIRY`, `PIN_CHANGE`, `CARD_BLOCK`, `CARD_UNBLOCK`, `TRANSFER` y `REVERSAL`.

Dado que el dataclass es `frozen=True`, ningún campo puede modificarse tras la creación. Para revertir una transacción, se crea una nueva transacción de tipo `REVERSAL` — la original nunca se altera.

#### `ATMMachine` — `src/twobank_atm/domain/entities/atm_machine.py`

Representa el hardware físico del cajero. Responsabilidades principales:

- Mantiene un `cash_inventory: dict[int, int]` que mapea denominación → cantidad
- `dispense_cash(amount, currency)` usa un algoritmo voraz de mayor a menor denominación
- Calcula `total_cash` como la suma de todos los valores del inventario
- Transiciona automáticamente al estado `OUT_OF_CASH` cuando el inventario llega a cero
- `load_cash(inventory)` restaura el inventario y transiciona de vuelta a `ACTIVE`
- `put_in_maintenance()` / `restore_from_maintenance()` para mantenimiento

---

### Excepciones de Dominio — `src/twobank_atm/domain/exceptions/domain_exceptions.py`

Todas las excepciones heredan de `TWOBankError(Exception)`. La jerarquía completa:

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

## Resultados de la Suite de Tests

Los 68 tests unitarios de dominio pasan. Tiempo de ejecución: **~0,2 segundos**.

```
pytest tests/unit/domain/ -v

platform win32 -- Python 3.14.4, pytest-9.0.3
collected 68 items

68 passed in 0.18s  ✅
```

### Cobertura de Tests por Archivo

| Archivo de Test | Clase Testeada | Tests | Todos Pasan |
|---|---|---|---|
| `test_money.py` | `Money` | 15 | ✅ |
| `test_currency.py` | `Currency` + `Currencies` | 10 | ✅ |
| `test_pin.py` | `Pin` | 8 | ✅ |
| `test_account.py` | `Account` | 12 | ✅ |
| `test_card.py` | `Card` | 9 | ✅ |
| `test_atm_machine.py` | `ATMMachine` | 10 | ✅ |
| `test_user.py` | `User` | 4 | ✅ |
| **Total** | | **68** | **✅ 100%** |

### Casos de Test Destacados

#### Precisión aritmética de Money
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

#### Bloqueo de tarjeta tras 3 intentos fallidos
```python
def test_three_failures_block_card(self):
    card = make_card()
    for _ in range(3):
        with pytest.raises(InvalidPinError):
            card.verify_pin("9999")
    with pytest.raises(CardBlockedError):
        card.verify_pin("1234")
```

#### Algoritmo voraz de dispensación del cajero
```python
def test_dispense_exact_amount(self):
    atm = make_atm()   # inventario: {50:10, 20:20, 10:30}
    result = atm.dispense_cash(Money.of(170, EUR))
    assert result == {50: 3, 20: 1}
```

---

## Problemas Encontrados y Resueltos

### Problema 1 — `ModuleNotFoundError: No module named 'src'`

**Síntoma:** pytest recogió 0 elementos debido a fallos de importación en todos los archivos de test.  
**Causa:** pytest no tenía la raíz del proyecto en `sys.path`.  
**Solución:** Se añadió `pythonpath = ["."]` a `[tool.pytest.ini_options]` en `pyproject.toml`.  
**Resultado:** pytest resolvió la raíz del proyecto pero seguía sin encontrar `src.domain`.

### Problema 2 — `ModuleNotFoundError: No module named 'src.domain'`

**Síntoma:** Tras la solución 1, pytest encontró `src` pero no `src.domain`.  
**Causa:** La estructura real del paquete es `src/twobank_atm/domain/`, no `src/domain/`. Todos los imports usaban el prefijo de ruta incorrecto.  
**Solución 1:** Se cambió `pythonpath` de `["."]` a `["src"]` en `pyproject.toml`.  
**Solución 2:** Se usó Find & Replace All de VS Code (`Ctrl+Shift+H`) para reemplazar todos los `from src.domain` → `from twobank_atm.domain` en toda la base de código.  
**Resultado:** Los 6 archivos de test se recogieron correctamente y 67/68 tests pasaron en la primera ejecución.

### Problema 3 — `test_expired_card_raises` — `ValueError` al crear la tarjeta

**Síntoma:** 1 test falló con `ValueError: Cannot issue a card with a past expiry date.`  
**Causa:** El test intentaba crear una tarjeta directamente con `expiry=date(2020, 1, 1)`, pero `Card.issue()` rechaza correctamente las fechas de caducidad pasadas en el momento de creación.  
**Solución:** Se modificó el test para crear primero una tarjeta válida y luego establecer manualmente `card.expiry_date = date(2020, 1, 1)` en la instancia antes de llamar a `verify_pin()`.  
**Resultado:** Los 68 tests pasando.

### Problema 4 — `IndentationError` en `test_card.py`

**Síntoma:** pytest no pudo recoger `test_card.py` con `IndentationError: expected an indented block after function definition on line 69`.  
**Causa:** Durante la corrección del Problema 3, el cuerpo del método se pegó sin la indentación de 4 espacios requerida, dejando una definición de función vacía.  
**Solución:** Se reescribió el método completo con la indentación correcta.  
**Resultado:** Los 68 tests pasando. ✅

### Problema 5 — `DeprecationWarning: datetime.utcnow() is deprecated`

**Síntoma:** 11 advertencias de deprecación aparecieron tras pasar todos los tests.  
**Causa:** `datetime.utcnow()` fue eliminado en Python 3.12. El código lo usaba en campos `default_factory`.  
**Solución:** Se reemplazaron todas las ocurrencias con `lambda: datetime.now(timezone.utc)` y se añadió `timezone` a los imports relevantes.  
**Resultado:** 0 advertencias en ejecuciones posteriores.

---

## Cómo Ejecutar los Tests

```powershell
# Activar el entorno virtual (Windows)
.\.venv\Scripts\Activate.ps1

# Ejecutar todos los tests unitarios de dominio con salida detallada
pytest tests/unit/domain/ -v

# Ejecutar con informe de cobertura
pytest tests/unit/domain/ -v --cov=src/twobank_atm/domain --cov-report=term-missing

# Ejecutar un único archivo de test
pytest tests/unit/domain/test_money.py -v

# Ejecutar un test concreto por nombre
pytest tests/unit/domain/test_card.py::TestPinVerification::test_three_failures_block_card -v
```

---

## Entorno

| Componente | Versión |
|---|---|
| Python | 3.14.4 |
| pytest | 9.0.3 |
| pytest-cov | 7.1.0 |
| pytest-mock | 3.15.1 |
| pluggy | 1.6.0 |
| Plataforma | Windows 11 (win32) |

---

## Próximos Pasos

La capa de dominio está completa y completamente testeada. Las siguientes capas están pendientes de implementación en orden:

1. **Capa de aplicación** (`src/twobank_atm/application/`) — casos de uso: `WithdrawCashUseCase`, `CheckBalanceUseCase`, `ChangePinUseCase`, `DepositCashUseCase`
2. **Capa de infraestructura** (`src/twobank_atm/infrastructure/`) — repositorios en memoria que implementan las interfaces de la capa de aplicación
3. **Capa de presentación** (`src/twobank_atm/presentation/`) — menú CLI con flujo de sesión del cajero
4. **Tests de integración** — testeo de casos de uso con adaptadores de infraestructura reales
5. **Tests end-to-end** — simulación completa de sesión de cajero

