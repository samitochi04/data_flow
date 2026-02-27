# Phase 1: Database Connection & User Model - Testing Guide

## Overview
This document outlines how to test the foundational setup of the DataFlow API, including database connection and the User model.

## Prerequisites
1. PostgreSQL is running and accessible
2. Python virtual environment is activated
3. Dependencies are installed

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Environment Configuration
Ensure `.env` file exists with correct database credentials:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataflow
POSTGRES_USER=dataflow_user
POSTGRES_PASSWORD=dataflow_pass
```

### 3. Test Database Connection

#### Option A: Run the Application
```bash
cd dataflow-server
python -m app.main
```

Expected output:
```
🚀 App starting... creating tables
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Option B: Check Tables via Debug Endpoint
Once the app is running:

1. Navigate to: `http://localhost:8000/health`
   - Should return: `{"status": "Ok"}`

2. Navigate to: `http://localhost:8000/debug/tables`
   - Should show the `users` table in the list

## Testing User Model via Scalar API

### 1. Access Scalar Documentation
- URL: `http://localhost:8000/scalar`
- This provides an interactive UI to test all API endpoints

### 2. Test User Registration Endpoint
**Endpoint**: `POST /users/register`

**Request Body**:
```json
{
  "name": "John Admin",
  "email": "admin@example.com",
  "password": "SecurePassword123"
}
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "name": "John Admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "last_login_at": null,
  "created_at": "2024-02-24T12:00:00+00:00",
  "updated_at": "2024-02-24T12:00:00+00:00"
}
```

### 3. Test User Login Endpoint
**Endpoint**: `POST /users/login`

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123"
}
```

**Expected Response** (200 OK):
```json
{
  "access_token": "1",
  "token_type": "bearer"
}
```

### 4. Test Error Scenarios

#### Duplicate Email Registration
**Endpoint**: `POST /users/register`
**Request**: Register with same email again
**Expected**: 400 Bad Request with message "User with this email already exists"

#### Invalid Credentials
**Endpoint**: `POST /users/login`
**Request**: 
```json
{
  "email": "admin@example.com",
  "password": "WrongPassword"
}
```
**Expected**: 401 Unauthorized with message "Invalid email or password"

#### Invalid Email Format
**Request**: 
```json
{
  "name": "Test User",
  "email": "not-an-email",
  "password": "Password123"
}
```
**Expected**: 422 Unprocessable Entity (validation error)

## Testing via FastAPI Test Client (Automated)

### 1. Create Test File
Create `tests/test_phase1_users.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.database import get_db, Base


@pytest.fixture
async def test_db():
    # Create test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal()
    await engine.dispose()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


@pytest.mark.asyncio
async def test_user_registration(client, test_db):
    response = client.post(
        "/users/register",
        json={
            "name": "Test Admin",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test Admin"
    assert data["role"] == "admin"
    assert "id" in data


@pytest.mark.asyncio
async def test_duplicate_email(client, test_db):
    # Register first user
    client.post(
        "/users/register",
        json={
            "name": "Test Admin",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/users/register",
        json={
            "name": "Another Admin",
            "email": "test@example.com",
            "password": "AnotherPassword123"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_user_login(client, test_db):
    # Register user
    client.post(
        "/users/register",
        json={
            "name": "Test Admin",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    
    # Login
    response = client.post(
        "/users/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_login(client, test_db):
    response = client.post(
        "/users/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]
```

### 2. Run Tests
```bash
pytest tests/test_phase1_users.py -v
```

### 3. Expected Test Results
```
test_phase1_users.py::test_health_check PASSED
test_phase1_users.py::test_user_registration PASSED
test_phase1_users.py::test_duplicate_email PASSED
test_phase1_users.py::test_user_login PASSED
test_phase1_users.py::test_invalid_login PASSED
```

## Manual Testing Checklist

- [ ] App starts without errors
- [ ] Health check endpoint works
- [ ] Debug endpoint lists tables
- [ ] Can register a new user via Scalar
- [ ] User data is returned with all fields
- [ ] Can login with correct credentials
- [ ] Cannot login with wrong password
- [ ] Cannot register duplicate email
- [ ] Password is properly hashed (verify in DB)
- [ ] Invalid email format is rejected
- [ ] Password too short is rejected
- [ ] All timestamps are in correct format

## Database Verification

### 1. Connect to PostgreSQL
```bash
psql -U dataflow_user -d dataflow -h localhost
```

### 2. Check Users Table
```sql
SELECT * FROM users;
```

Expected structure:
```
 id |    name     |       email       | password_hash | role  | is_active | last_login_at |         created_at         |         updated_at
----+-------------+-------------------+---------------+-------+-----------+---------------+----------------------------+----------------------------
  1 | John Admin  | admin@example.com | $2b$12$...    | admin | t         |               | 2024-02-24 12:00:00+00:00 | 2024-02-24 12:00:00+00:00
```

### 3. Verify Password Hashing
```sql
SELECT id, email, password_hash FROM users;
```
- Password hash should start with `$2b$12$` (bcrypt format)
- Should NOT be plain text

## Troubleshooting

### Issue: "Could not connect to database"
**Solution**: 
- Verify PostgreSQL is running
- Check .env credentials
- Verify network connectivity to database host

### Issue: "No module named 'app'"
**Solution**:
- Ensure you're in the correct directory
- Run with `python -m` instead of `python`

### Issue: "Import error: No module named 'bcrypt'"
**Solution**:
```bash
pip install bcrypt passlib
```

### Issue: "Pydantic validation error"
**Solution**:
- Check email format (must be valid)
- Check password length (minimum 8 characters)
- Check all required fields are provided

## Next Steps

Once Phase 1 is verified:
1. Phase 2: Authentication & JWT tokens
2. Phase 3: Content Management (Blog Posts)
3. Phase 4: Comments & Likes
4. Phase 5: Analytics Tracking
5. ... and so on (see server.md for full roadmap)

## Phase 1 Completion Criteria

✅ **Must have:**
- [x] User model with all required fields
- [x] Pydantic schemas for validation
- [x] User registration endpoint
- [x] User login endpoint
- [x] Password hashing working
- [x] Database connection verified
- [x] Tables created on startup
- [x] Can register and login via Scalar API

**Status**: Phase 1 Complete - Ready for Phase 2
