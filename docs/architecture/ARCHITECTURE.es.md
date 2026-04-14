# TWO Bank ATM — Documento de Arquitectura

> **The Worldwide One Bank** | Referencia de Arquitectura v1.0.0  
> Idioma: [English 🇬🇧 → ARCHITECTURE.md] · **[Español 🇪🇸]**  
> Última actualización: Abril 2026 · Python 3.14 · Clean Architecture

---

## Resumen

TWO Bank ATM es una simulación de cajero automático desarrollada en Python siguiendo los principios de **Clean Architecture**, definidos por Robert C. Martin. El sistema está estructurado en cuatro capas concéntricas donde cada capa depende únicamente de la capa directamente interior — nunca hacia afuera. Esta regla, conocida como la **Regla de Dependencia**, garantiza que la lógica de negocio quede completamente aislada de frameworks, bases de datos y mecanismos de entrega.

El objetivo principal de esta arquitectura es la mantenibilidad a largo plazo: las reglas bancarias del núcleo pueden testarse, comprenderse y modificarse de forma independiente a cualquier decisión de infraestructura técnica.

---

## Las Cuatro Capas

```
┌─────────────────────────────────────────────────────┐
│             PRESENTACIÓN (Capa 4)                   │
│         CLI · UI · API · Puntos de entrada          │
├─────────────────────────────────────────────────────┤
│            INFRAESTRUCTURA (Capa 3)                 │
│      Base de datos · Sistema de archivos · APIs     │
├─────────────────────────────────────────────────────┤
│              APLICACIÓN (Capa 2)                    │
│         Casos de uso · Servicios · DTOs             │
├─────────────────────────────────────────────────────┤
│                DOMINIO (Capa 1)                     │
│    Entidades · Value Objects · Reglas de negocio    │
└─────────────────────────────────────────────────────┘

        Dirección de dependencia: SOLO HACIA DENTRO →
```

### Capa 1 — Dominio

La capa más interna. Contiene todas las reglas de negocio, entidades, value objects y excepciones de dominio. Esta capa tiene **cero dependencias** de librerías externas o frameworks — es Python puro. Los cambios en la base de datos, el CLI o cualquier servicio externo no pueden afectar a esta capa.

### Capa 2 — Aplicación

Contiene los casos de uso — cada uno representa una acción de usuario (p. ej., `WithdrawCashUseCase`, `CheckBalanceUseCase`). Los casos de uso orquestan objetos de dominio y definen las interfaces (protocolos de repositorio) que la capa de infraestructura debe implementar.

### Capa 3 — Infraestructura

Implementa las interfaces definidas en la capa de aplicación. Contiene los adaptadores de base de datos reales, el acceso al sistema de archivos, los clientes de API de divisas externas y cualquier otro código con I/O.

### Capa 4 — Presentación

La capa más externa. Contiene el menú CLI, la gestión de entrada del usuario y el formateo de salida. Esta capa llama a los casos de uso y nunca interactúa con el dominio directamente.

---

## Arquitectura de la Capa de Dominio

La capa de dominio es el corazón del sistema. Se divide en tres categorías de objetos.

### Value Objects

Objetos inmutables identificados únicamente por su valor. Dos instancias con los mismos datos se consideran iguales e intercambiables.

| Clase | Archivo | Responsabilidad |
|---|---|---|
| `Money` | `value_objects/money.py` | Representa una cantidad monetaria exacta con su divisa. Usa `Decimal` para precisión. Soporta aritmética y comparación. |
| `Currency` | `value_objects/currency.py` | Representa una divisa ISO 4217 (código, símbolo, nombre). Se normaliza a mayúsculas al crearse. |
| `Currencies` | `value_objects/currencies.py` | Catálogo de todas las divisas soportadas: EUR, USD, GBP, JPY, CHF, BTC. Proporciona búsqueda con `from_code()`. |
| `Pin` | `value_objects/pin.py` | Almacena un PIN hasheado + con salt. El valor real nunca se conserva. Proporciona `verify()` para comparación segura. |

**Decisión de diseño clave — `Decimal` en lugar de `float`:** La aritmética de coma flotante no puede representar ciertos valores decimales de forma exacta. En banca, incluso un error de redondeo de `0,0000001` es inaceptable. Todas las cantidades monetarias usan `decimal.Decimal` con cuantización `ROUND_HALF_UP` a 2 decimales.

**Decisión de diseño clave — Seguridad del PIN:**
- `hashlib.sha256` hashea el PIN con un salt criptográfico
- `secrets.token_hex(16)` genera un salt único por instancia de PIN, neutralizando ataques de tablas arcoíris
- `secrets.compare_digest` compara hashes en tiempo constante, previniendo ataques de timing

### Entidades

Objetos mutables identificados por un ID único en lugar de sus datos. Dos cuentas con el mismo saldo siguen siendo cuentas distintas.

| Clase | Archivo | Responsabilidad |
|---|---|---|
| `Account` | `entities/account.py` | Cuenta bancaria con saldo, divisa y estado. Aplica las reglas de negocio para depósito y retiro. |
| `Card` | `entities/card.py` | Tarjeta bancaria vinculada a una cuenta. Gestiona la verificación del PIN con bloqueo tras 3 intentos fallidos. |
| `User` | `entities/user.py` | Cliente del banco. Almacena referencias (UUIDs) a sus tarjetas y cuentas. Normaliza nombre y email al crearse. |
| `Transaction` | `entities/transaction.py` | Registro inmutable de una operación en el cajero. Se congela tras su creación — los registros son permanentes. |
| `ATMMachine` | `entities/atm_machine.py` | Cajero físico. Gestiona el inventario de efectivo y dispensa billetes usando un algoritmo voraz de mayor a menor denominación. |

**Decisión de diseño clave — `User` almacena IDs, no objetos:** La capa de dominio nunca mantiene referencias directas a otras entidades activas. `User.card_ids` es una `list[UUID]`, no una `list[Card]`. Esto mantiene el dominio libre de dependencias de repositorios e impide la formación de grafos de objetos profundos.

**Decisión de diseño clave — `Transaction` está congelada:** Una `Transaction` usa `@dataclass(frozen=True)`, haciéndola inmutable como un value object. Los registros financieros nunca deben modificarse tras su creación. Para revertir una operación, se registra una nueva transacción de tipo `REVERSED` en lugar de alterar la original.

### Excepciones de Dominio

Una jerarquía de excepciones personalizadas que representan violaciones de reglas de negocio. Todas heredan de `TWOBankError`, que hereda de `Exception`.

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

**Decisión de diseño clave — Jerarquía de excepciones personalizada:** Usar `TWOBankError` como base permite a la capa de presentación capturar todos los errores bancarios con un único `except TWOBankError`, mientras permite un manejo más fino en capas inferiores. También evita que las excepciones de infraestructura (p. ej., `sqlalchemy.exc.IntegrityError`) escapen al dominio.

---

## Algoritmo de Dispensación de Efectivo

El método `ATMMachine.dispense_cash()` implementa un algoritmo voraz que dispensa efectivo usando **primero la denominación más grande disponible**. Esto minimiza el número de billetes dispensados y reproduce el comportamiento real de un cajero.

**Ejemplo:** Solicitud de €170 con inventario `{50: 10, 20: 20, 10: 30}`:

```
Paso 1: 170 ÷ 50 = 3 billetes  → restante: 170 - 150 = 20
Paso 2:  20 ÷ 20 = 1 billete   → restante:  20 -  20 =  0  ✓

Resultado: { 50: 3, 20: 1 }  →  3 × €50 + 1 × €20 = €170
```

El algoritmo opera en tres fases:
1. **Calcular** — determinar la combinación de billetes sin modificar el inventario
2. **Validar** — si `restante > 0` tras todas las denominaciones, lanzar `ATMInsufficientCashError`
3. **Confirmar** — solo descontar del inventario tras superar la validación

Este enfoque de tres fases garantiza que el inventario del cajero nunca se descuente parcialmente en una operación de dispensación fallida.

---

## Ciclo de Vida de la Sesión del Cajero

```
    [INACTIVO] ── tarjeta insertada ──→ [EN_SESIÓN]
         ↑                                   │
         └──────── tarjeta expulsada ─────────┘
         │
         ├── llamada de mantenimiento ──→ [MANTENIMIENTO] ── restaurar ──→ [INACTIVO]
         │
         └── último billete dispensado ──→ [SIN_EFECTIVO] ── cargar ──→ [INACTIVO]
```

---

## Estructura del Proyecto

```
TWO-Bank-The-Worldwide-Only-Bank-ATM-Project/
│
├── src/twobank_atm/
│   ├── domain/
│   │   ├── entities/          ← Account, Card, User, Transaction, ATMMachine
│   │   ├── value_objects/     ← Money, Currency, Currencies, Pin
│   │   └── exceptions/        ← domain_exceptions.py
│   │
│   ├── application/           ← Casos de uso (Capa 2) — pendiente
│   ├── infrastructure/        ← Adaptadores BD, APIs (Capa 3) — pendiente
│   └── presentation/          ← CLI (Capa 4) — pendiente
│
├── tests/
│   ├── unit/domain/           ← 68 tests de dominio — todos pasando ✅
│   ├── unit/application/      ← pendiente
│   ├── integration/           ← pendiente
│   └── e2e/                   ← pendiente
│
├── docs/
│   └── architecture/          ← este documento
│
├── pyproject.toml
├── main.py
└── README.md
```

---

## Stack Tecnológico

| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python 3.14 | Type hints, dataclasses, sentencias `match` |
| Precisión monetaria | `decimal.Decimal` | Aritmética exacta — sin errores de coma flotante |
| IDs únicos | `uuid.UUID` / `uuid4()` | Identificadores de entidad estándar y sin colisiones |
| Hash de PIN | `hashlib.sha256` + `secrets` | Seguridad criptográfica estándar del sector |
| Modelado de datos | `@dataclass` / `frozen=True` | Value objects concisos e inmutables |
| Testing | `pytest` + `pytest-cov` | 68 tests unitarios de dominio — 100% de éxito |
| Verificación de tipos | `mypy` | Análisis estático que refuerza la Regla de Dependencia |
| CI/CD | GitHub Actions | Lint, type-check y tests automáticos en cada push |

---

## Registros de Decisiones Arquitectónicas

Los documentos ADR completos se encuentran en `docs/adr/`.

| ADR | Decisión |
|---|---|
| ADR-001 | Clean Architecture elegida frente a arquitectura por capas (MVC) |
| ADR-002 | `decimal.Decimal` en lugar de `float` para todos los valores monetarios |
| ADR-003 | UUID como clave primaria para todas las entidades |
| ADR-004 | Documentación bilingüe (inglés + español) |

