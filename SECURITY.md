# Security Policy — TWO Bank ATM

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Security Architecture

### PIN Storage
- PINs are **never** stored in plain text
- All PINs are hashed using **bcrypt** with cost factor 12
- Each PIN hash includes a unique salt (built into bcrypt)
- Verification uses `bcrypt.checkpw()` — the plain PIN is discarded immediately

### Session Security
- Sessions expire after **90 seconds** of inactivity
- Cards are **blocked** after 3 consecutive failed PIN attempts
- Blocked cards require admin intervention to unblock

### Secrets Management
- All secrets (API keys, DB paths) are stored in `.env` files
- `.env` is listed in `.gitignore` — **never committed**
- Use `.env.example` as a template (contains no real secrets)

### Database
- SQLite database file is stored in `data/` (git-ignored)
- All financial amounts stored as **integer cents** to prevent precision errors

## Reporting a Vulnerability

If you discover a security vulnerability, please open a **private** GitHub
Security Advisory rather than a public issue.

Do **not** include sensitive information (real PINs, account numbers) in any
public issue or pull request.
