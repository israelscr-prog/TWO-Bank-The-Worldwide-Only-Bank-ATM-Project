# Política de Seguridad — TWO Bank ATM

## Versiones Soportadas

| Versión | Soportada |
|---------|-----------|
| 0.1.x   | ✅ Sí     |

---

## Arquitectura de Seguridad

### Almacenamiento del PIN
- Los PINs **nunca** se almacenan en texto plano
- Todos los PINs se hashean con **bcrypt** con factor de coste 12
- Cada hash incluye una sal única (integrada en bcrypt)
- La verificación usa `bcrypt.checkpw()` — el PIN en texto plano se descarta inmediatamente

### Seguridad de Sesión
- Las sesiones expiran tras **90 segundos** de inactividad
- Las tarjetas se **bloquean** tras 3 intentos de PIN fallidos consecutivos
- Las tarjetas bloqueadas requieren intervención del administrador para desbloquearse

### Gestión de Secretos
- Todos los secretos (claves API, rutas de BD) se almacenan en archivos `.env`
- `.env` está en `.gitignore` — **nunca se hace commit**
- Usa `.env.example` como plantilla (no contiene secretos reales)

### Base de Datos
- El archivo de base de datos SQLite se almacena en `data/` (ignorado por git)
- Todos los importes financieros se almacenan como **centavos enteros** para evitar errores de precisión

---

## Notificación de Vulnerabilidades

Si descubres una vulnerabilidad de seguridad, por favor abre un **Aviso de Seguridad privado**
en GitHub en lugar de un issue público.

**No incluyas** información sensible (PINs reales, números de cuenta) en ningún
issue o pull request público.