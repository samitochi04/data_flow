"""Tests for user registration and authentication endpoints"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


def test_user_registration(client: TestClient):
    """Test user registration endpoint"""
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


def test_duplicate_email(client: TestClient):
    """Test duplicate email registration rejection"""
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


def test_user_login(client: TestClient):
    """Test user login endpoint"""
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


def test_invalid_login(client: TestClient):
    """Test invalid login credentials"""
    response = client.post(
        "/users/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_invalid_email_format(client: TestClient):
    """Test invalid email format rejection"""
    response = client.post(
        "/users/register",
        json={
            "name": "Test User",
            "email": "not-an-email",
            "password": "Password123"
        }
    )
    assert response.status_code == 422


def test_short_password(client: TestClient):
    """Test password too short rejection"""
    response = client.post(
        "/users/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "short"
        }
    )
    assert response.status_code == 422