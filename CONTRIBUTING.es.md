# Guía de Contribución — TWO Bank ATM

Gracias por contribuir a TWO Bank ATM — El Banco Mundial Único.
Por favor, lee estas directrices antes de enviar cualquier código.

---

## 🌿 Estrategia de Ramas

main ← Solo código listo para producción. Protegida.
develop ← Rama de integración. Todas las funcionalidades se fusionan aquí.
feature/* ← Nuevas funcionalidades. Parte de develop.
fix/* ← Corrección de errores. Parte de develop.
hotfix/* ← Correcciones críticas en producción. Parte de main.

text

### Ejemplos de nombres de rama
```bash
git checkout -b feature/caso-uso-retirada-efectivo
git checkout -b feature/value-object-money
git checkout -b fix/error-validacion-pin
git checkout -b hotfix/crash-timeout-sesion
```

---

## 📝 Formato de Mensajes de Commit

Cada mensaje de commit debe seguir esta estructura:

<tipo>(<ámbito>): <descripción corta>

[cuerpo opcional]
[pie opcional]

text

### Tipos
| Tipo | Cuándo usarlo |
|------|--------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de error |
| `test` | Añadir o corregir pruebas |
| `docs` | Solo documentación |
| `refactor` | Reestructuración sin cambio de comportamiento |
| `style` | Solo formato (Black, Ruff) |
| `chore` | Herramientas, dependencias, configuración |

### Ejemplos

feat(domain): añadir value object Money con almacenamiento en centavos enteros
fix(auth): corregir reinicio del contador de intentos de PIN
test(domain): añadir pruebas unitarias de validación de saldo en Account
docs(readme): actualizar instrucciones de instalación para Windows
refactor(withdrawal): extraer lógica de denominaciones a la entidad ATMMachine
chore(deps): actualizar bcrypt a 4.2.0

text

---

## 🏗️ Estándares de Código

Todo el código debe seguir las reglas de [`docs/DOCUMENTATION_RULES.es.md`](docs/DOCUMENTATION_RULES.es.md).

### Lista de comprobación antes de cada commit

- [ ] Cada función tiene docstring (descripción, Args, Returns, Raises)
- [ ] Cada módulo tiene docstring de nivel de módulo (Module, Layer, Description, Author)
- [ ] Type hints en todos los parámetros y valores de retorno
- [ ] Sin números mágicos — usar `constants.py`
- [ ] Sin cadenas hardcodeadas en la UI — usar `t.get("clave")`
- [ ] Todo código nuevo tiene pruebas unitarias
- [ ] `black src/ tests/` pasa sin cambios
- [ ] `ruff check src/ tests/` pasa sin errores

---

## 🧪 Requisitos de Pruebas

Cada nueva funcionalidad debe incluir pruebas antes de que un PR pueda fusionarse.

```bash
# Ejecutar antes de enviar un PR
pytest tests/unit/ -v           # Deben pasar todas
pytest tests/integration/ -v    # Deben pasar todas
pytest --cov=src/twobank_atm --cov-report=term-missing
# La cobertura no debe bajar del 80%
```

### Estructura de pruebas (DADO / CUANDO / ENTONCES)
```python
def test_retirada_reduce_saldo():
    # DADO
    account = Account(balance=Money(10000, "EUR"))  # 100,00 €

    # CUANDO
    account.debit(Money(3000, "EUR"))               # 30,00 €

    # ENTONCES
    assert account.balance == Money(7000, "EUR")    # 70,00 €
```

---

## 🔄 Proceso de Pull Request

1. Asegúrate de que todas las pruebas pasan en local
2. Actualiza la documentación si ha cambiado el comportamiento
3. Rellena la plantilla del PR completamente
4. Solicita revisión de al menos un miembro del equipo
5. Aplasta commits antes de fusionar con develop

---

## 🚫 Lo que NO se debe hacer

- Nunca hacer commit de archivos `.env` ni secretos
- Nunca escribir importes en EUR como float (`50.25`) — usar centavos enteros (`5025`)
- Nunca añadir cadenas de UI directamente — usar el traductor
- Nunca omitir el `__init__.py` en una nueva carpeta de paquete
- Nunca romper la regla de dependencia (las capas externas no pueden importar las internas)

---

## 🆘 ¿Preguntas?

Abre un Issue de GitHub con la etiqueta `question`.