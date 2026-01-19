# Testing Guide

This document describes the testing strategy, structure, and conventions used in the **Video Sharing Application** backend. It is intended for contributors and reviewers to understand *how* and *why* tests are written the way they are.

---

## 1. Testing Philosophy

Our testing approach follows these principles:

- **Black-box API testing** over internal implementation details
- **Isolation first**: each test must run independently
- **No real external services** (ImageKit, email, cloud, etc.)
- **Production-like execution** using FastAPI lifespan events
- **Fail fast and loudly** when assumptions break

We prioritize **confidence and safety** over sheer test count.

---

## 2. Test Stack

| Layer | Tool |
|------|------|
| Test runner | `pytest` |
| Async support | `pytest-asyncio`, `pytest-anyio` |
| HTTP client | `httpx.AsyncClient` |
| App lifecycle | `asgi-lifespan` |
| Dependency overrides | FastAPI `dependency_overrides` |

---

## 3. Test Directory Structure

```
/tests
├── api/
│   └── test_health.py
│   └── v1/
│       ├── test_posts_upload.py
│       ├── test_posts_delete.py
│       └── test_feed.py
│       └── test_auth.py
├── conftest.py
└── __init__.py
```

### Why this structure?

- Mirrors API versioning (`/api/v1/...`)
- Keeps upload/delete/feed concerns isolated
- Avoids "mega test files"
- Encourages focused assertions

---

## 4. `conftest.py` Responsibilities

`conftest.py` acts as the **testing backbone**. It provides:

### Core Fixtures

- `async_client` – lifecycle-aware HTTP client
- `auth_user` – factory for creating authenticated users
- `auth_headers` – default test user authentication
- Path helpers (`posts_path_v1`, `feed_path_v1`, etc.)

### Why factories instead of globals?

Factories allow:
- Multiple users per test
- Ownership testing (403s)
- Feed behavior across users

---

## 5. External Service Mocking (ImageKit)

### Problem

The `/posts/upload` endpoint depends on ImageKit:

- Network calls
- API keys
- Expiring credentials

These **must never** run during tests.

### Solution: Dependency Override

We override `get_imagekit` at the FastAPI dependency level:

```python
app.dependency_overrides[get_imagekit] = lambda: FakeImageKit()
```

### FakeImageKit Behavior

- Mimics `imagekit.files.upload(...)`
- Returns deterministic `url` and `name`
- Touches **no real code paths** in ImageKit

This ensures:

- Tests are fast
- Tests are deterministic
- CI never fails due to external services

---

## 6. Writing Tests: Conventions

### Naming

- Test files: `test_<feature>.py`
- Test functions: `test_<behavior>_<expectation>`

Example:

```python
def test_feed_is_ordered_by_created_at_desc(...):
```

---

### Structure

Each test follows **Arrange → Act → Assert**:

```python
# Arrange
headers = await auth_user()

# Act
response = await async_client.post(...)

# Assert
assert response.status_code == 201
```

---

## 7. Multi-User Testing

To test authorization and ownership:

```python
user1 = await auth_user()
user2 = await auth_user()
```

Used for:
- Delete permissions
- `is_owner` flags
- Feed visibility

---

## 8. CI Integration

Tests are executed automatically using **GitHub Actions**.

### Trigger Conditions

- Push to `main`
- Pull request targeting `main`

### CI Guarantees

- Clean Linux VM
- Fresh dependencies
- No local state leakage
- Full test isolation

A failing test **blocks confidence**, not deployment.

---

## 9. What We Do NOT Test (Intentionally)

We intentionally avoid:

- ImageKit SDK behavior
- SQLAlchemy internals
- FastAPI internals
- Third-party authentication libraries

Those are assumed correct and tested upstream.

---

## 10. Guiding Principle

> **If a test fails, it should tell you *exactly* what broke and *why*.**

No flaky tests.
No hidden dependencies.
No magic.

---

## 11. Final Notes

- Tests are part of the product
- CI is a safety net, not a burden
- Clean tests enable fearless refactoring

If you feel unsure about a test:
**simplify it** — clarity beats cleverness.
