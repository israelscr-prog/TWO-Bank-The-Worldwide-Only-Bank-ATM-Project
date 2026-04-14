<p align="right">
  <a href="./README.md">English</a> | <a href="./README.es.md">Español</a>
</p>

# 🏦 TWO Bank ATM
### El Banco Mundial Único

> Una simulación profesional de un cajero automático construida con Python 3.14,
> Clean Architecture, soporte bilingüe completo (inglés y español) y una tubería CI/CD.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-orange)
![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow)
![Tests](https://img.shields.io/badge/Tests-Unit%20%7C%20Integration%20%7C%20E2E-purple)
![i18n](https://img.shields.io/badge/Languages-EN%20%7C%20ES-red)

</div>

---

## 📋 Tabla de Contenidos

- [Sobre el Proyecto](#-sobre-el-proyecto)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Primeros Pasos](#-primeros-pasos)
- [Ejecución de Pruebas](#-ejecución-de-pruebas)
- [Variables de Entorno](#-variables-de-entorno)
- [Hoja de Ruta](#-hoja-de-ruta)
- [Contribuir](#-contribuir)
- [Equipo](#-equipo)
- [Licencia](#-licencia)

---

## 🎯 Sobre el Proyecto

**TWO Bank ATM** es un sistema de software de cajero automático con todas las funciones,
diseñado y construido desde cero usando principios profesionales de ingeniería de software.

El proyecto demuestra Clean Architecture, patrones inspirados en Domain-Driven Design,
principios SOLID, internacionalización bilingüe completa, manejo seguro de PIN
y una tubería CI/CD completa, todo en Python 3.14.

Este proyecto se construye de forma progresiva, capa por capa, siguiendo buenas
prácticas utilizadas en el desarrollo de software bancario del mundo real.

---

## ✨ Características

| Característica | Estado | Descripción |
|---------|--------|-------------|
| 🔐 Autenticación | 🔲 Planificado | Número de tarjeta + PIN cifrado con bcrypt |
| 💶 Retirada de efectivo | 🔲 Planificado | Dispensación con múltiples denominaciones (€5/€10/€20/€50) |
| 💰 Ingreso de efectivo | 🔲 Planificado | Ingreso con actualización inmediata del saldo |
| 📊 Consulta de saldo | 🔲 Planificado | Visualización del saldo disponible en tiempo real |
| 🔄 Transferencias | 🔲 Planificado | Transferencias entre cuentas |
| 📋 Mini extracto | 🔲 Planificado | Últimos 10 movimientos con comprobante |
| 💱 Conversor de divisas | 🔲 Planificado | Tipos en vivo: EUR → USD, GBP, JPY, CHF, BTC |
| 🔑 Cambio de PIN | 🔲 Planificado | Cambio seguro de PIN con confirmación |
| 🛡️ Panel de administración | 🔲 Planificado | Crear/bloquear cuentas, ver inventario |
| 🌍 Interfaz bilingüe | ✅ Listo | Soporte completo en inglés y español |
| ⏱️ Tiempo de sesión | 🔲 Planificado | Cierre automático tras 90 segundos de inactividad |
| 🔒 Bloqueo de tarjeta | 🔲 Planificado | Bloqueo tras 3 intentos fallidos consecutivos |

---

## 🏗️ Arquitectura

Este proyecto sigue **Clean Architecture**, un modelo de 4 capas donde las dependencias
solo apuntan **hacia adentro**. La lógica de negocio está completamente aislada de bases
de datos, APIs e interfaces de usuario.

```text
┌─────────────────────────────────────────────────┐
│           CAPA 4 — PRESENTACIÓN                 │
│        CLI (Fase 1) · GUI (Fase 2)              │
├─────────────────────────────────────────────────┤
│           CAPA 3 — INFRAESTRUCTURA              │
│       SQLite · bcrypt · ExchangeRate API        │
├─────────────────────────────────────────────────┤
│           CAPA 2 — APLICACIÓN                   │
│        Casos de Uso · Puertos · DTOs            │
├─────────────────────────────────────────────────┤
│           CAPA 1 — DOMINIO  ← núcleo            │
│   Entidades · Value Objects · Excepciones       │
│         Cero dependencias externas              │
└─────────────────────────────────────────────────┘
```

### Decisiones arquitectónicas clave

| Decisión | Elección | Motivo |
|----------|--------|--------|
| Base de datos | SQLite | Sin servidor, SQL real, portable |
| Seguridad del PIN | bcrypt cost=12 | Estándar de industria, resistente a fuerza bruta |
| Manejo del dinero | Centavos enteros | Cero errores de coma flotante |
| i18n | Archivos JSON | Legibles, sin compilación, fáciles de ampliar |
| Arquitectura | Clean Architecture | Testeable, capas intercambiables, SOLID |

> 📖 Justificación completa en [`docs/decisions/`](./docs/decisions/)

---

## 📁 Estructura del Proyecto

```text
TWO-Bank-ATM/
│
├── main.py                        ← Punto único de entrada
├── requirements.txt               ← Todas las dependencias
├── pyproject.toml                 ← Configuración del proyecto y herramientas
├── .env.example                   ← Plantilla de variables de entorno
│
├── .github/workflows/             ← Tubería CI/CD (GitHub Actions)
├── .vscode/                       ← Configuración de VS Code y debug
│
├── src/twobank_atm/
│   ├── domain/                    ← Capa 1: lógica de negocio pura
│   │   ├── entities/              ← Account, Card, User, Transaction, ATM
│   │   ├── value_objects/         ← Money, Currency, Pin (inmutables)
│   │   └── exceptions/            ← Errores específicos del dominio
│   │
│   ├── application/               ← Capa 2: casos de uso y contratos
│   │   ├── use_cases/             ← Un archivo por acción del ATM
│   │   ├── ports/                 ← Interfaces abstractas
│   │   └── dtos/                  ← Data Transfer Objects
│   │
│   ├── infrastructure/            ← Capa 3: implementaciones técnicas
│   │   ├── database/              ← SQLite, migraciones, repositorios
│   │   ├── security/              ← bcrypt, gestión de sesiones
│   │   ├── services/              ← API de divisas, generador de recibos
│   │   └── seeders/               ← Datos de prueba
│   │
│   ├── presentation/              ← Capa 4: interfaces de usuario
│   │   ├── cli/                   ← Interfaz terminal (Fase 1)
│   │   └── gui/                   ← Tkinter (Fase 2)
│   │
│   ├── i18n/                      ← Motor de internacionalización
│   │   └── locales/en/ + es/      ← Archivos de traducción
│   │
│   └── config/                    ← Configuración y constantes
│
├── tests/
│   ├── unit/                      ← Pruebas unitarias
│   ├── integration/               ← Pruebas de integración
│   └── e2e/                       ← Pruebas end-to-end
│
├── scripts/                       ← Scripts de base de datos
├── docs/                          ← Arquitectura, ADRs y guías
├── data/                          ← Base de datos SQLite
└── logs/                          ← Logs de ejecución
```

---

## 🚀 Primeros Pasos

### Requisitos previos

- Python 3.12 o superior (3.14 recomendado)
- Git
- VS Code con la extensión de Python

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/TWO-Bank-The-Worldwide-Only-Bank-ATM-Project.git
cd TWO-Bank-The-Worldwide-Only-Bank-ATM-Project

# 2. Crear y activar entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# o en macOS/Linux:
# cp .env.example .env

# 5. Ejecutar el proyecto
python main.py
```

### Salida esperada

```text
=============================================
   TWO Bank ATM - The Worldwide One Bank
=============================================
  Status: Project structure OK
  Next:   Building Domain layer...
=============================================
```

---

## 🧪 Ejecución de Pruebas

```bash
# Todas las pruebas
pytest

# Solo unitarias
pytest tests/unit/ -v

# Integración
pytest tests/integration/ -v

# End-to-end
pytest tests/e2e/ -v

# Con cobertura
pytest --cov=src/twobank_atm --cov-report=term-missing
```

---

## ⚙️ Variables de Entorno

Copia `.env.example` a `.env` y configura lo necesario:

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `DB_PATH` | `./data/twobank.db` | Ruta del archivo SQLite |
| `BCRYPT_ROUNDS` | `12` | Coste de bcrypt |
| `SESSION_TIMEOUT_SECONDS` | `90` | Tiempo máximo de inactividad |
| `MAX_PIN_ATTEMPTS` | `3` | Intentos fallidos antes de bloquear |
| `ATM_ID` | `ATM-001` | Identificador del cajero |
| `ATM_MAX_WITHDRAWAL_EUR` | `600` | Retirada máxima por operación |
| `ATM_DAILY_LIMIT_EUR` | `1200` | Límite diario |
| `EXCHANGE_RATE_API_KEY` | — | Clave para exchangerate-api.com |
| `DEFAULT_LANGUAGE` | `en` | Idioma por defecto |
| `LOG_LEVEL` | `INFO` | Nivel de logs |

---

## 🗺️ Hoja de Ruta

### Fase 1 — CLI (En progreso)
- [x] Estructura del proyecto y esqueleto Clean Architecture
- [x] Traducciones bilingües (EN + ES)
- [x] Tubería CI/CD
- [ ] Capa de dominio: Money, Account, Card, Transaction
- [ ] Capa de aplicación: todos los casos de uso
- [ ] Capa de infraestructura: SQLite, bcrypt, API de divisas
- [ ] Capa de presentación: pantallas CLI
- [ ] Suite completa de pruebas

### Fase 2 — GUI (Planificado)
- [ ] Interfaz gráfica con Tkinter
- [ ] Diseño tipo cajero automático
- [ ] Animación de inserción de tarjeta

---

## 🤝 Contribuir

Este es un proyecto de aprendizaje construido paso a paso. Toda contribución es bienvenida.

1. Haz un fork del repositorio
2. Crea una rama: `git checkout -b feature/tu-funcionalidad`
3. Sigue las reglas en [`docs/DOCUMENTATION_RULES.md`](./docs/DOCUMENTATION_RULES.md)
4. Escribe pruebas para tu código
5. Abre un Pull Request

> 📖 Consulta [`CONTRIBUTING.md`](./CONTRIBUTING.md) para más detalle.

---

## 👥 Equipo

| Rol | Nombre |
|------|------|
| Desarrollo principal | TWO Bank Dev Team |
| Arquitectura | Clean Architecture |
| Seguridad | bcrypt + OWASP |

---

## 📄 Licencia

Este proyecto está licenciado bajo MIT. Consulta [`LICENSE`](./LICENSE) para más detalle.

---

<div align="center">
  <sub>Construido con ❤️ usando Python 3.14 · Clean Architecture · Desarrollo guiado por pruebas</sub>
</div>
