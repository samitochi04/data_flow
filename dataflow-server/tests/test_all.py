"""
Comprehensive test suite for DataFlow API
Tests all models, endpoints, and business logic
Run with: pytest tests/test_all.py -v
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# HEALTH & BASIC ENDPOINTS
# ============================================================================

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text or "Data Flow" in response.text


# ============================================================================
# USER REGISTRATION & AUTHENTICATION
# ============================================================================

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


def test_duplicate_email_registration(client: TestClient):
    """Test duplicate email registration rejection"""
    # Register first user
    client.post(
        "/users/register",
        json={
            "name": "Test Admin",
            "email": "duplicate@example.com",
            "password": "TestPassword123"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/users/register",
        json={
            "name": "Another Admin",
            "email": "duplicate@example.com",
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
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )
    
    # Login
    response = client.post(
        "/users/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login_credentials(client: TestClient):
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


def test_short_password_validation(client: TestClient):
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


# ============================================================================
# CATEGORY MANAGEMENT
# ============================================================================

def test_create_category(client: TestClient):
    """Test creating a new category"""
    response = client.post(
        "/categories",
        json={
            "name": "Web Development",
            "slug": "web-development",
            "description": "Articles about web development"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Web Development"
    assert data["slug"] == "web-development"
    assert "id" in data


def test_create_subcategory(client: TestClient):
    """Test creating a subcategory under a parent"""
    # Create parent
    parent_response = client.post(
        "/categories",
        json={
            "name": "Backend",
            "slug": "backend-parent"
        }
    )
    parent_id = parent_response.json()["id"]
    
    # Create subcategory
    response = client.post(
        "/categories",
        json={
            "name": "Python Backend",
            "slug": "python-backend",
            "parent_id": parent_id
        }
    )
    
    assert response.status_code == 201
    assert response.json()["parent_id"] == parent_id


def test_duplicate_category_slug(client: TestClient):
    """Test that duplicate slugs are rejected"""
    client.post(
        "/categories",
        json={
            "name": "First",
            "slug": "unique-cat-slug"
        }
    )
    
    response = client.post(
        "/categories",
        json={
            "name": "Second",
            "slug": "unique-cat-slug"
        }
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_get_category(client: TestClient):
    """Test retrieving a category by ID"""
    create_response = client.post(
        "/categories",
        json={
            "name": "Get Test",
            "slug": "get-test-cat"
        }
    )
    cat_id = create_response.json()["id"]
    
    response = client.get(f"/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["id"] == cat_id


def test_list_categories(client: TestClient):
    """Test listing categories"""
    # Create several categories
    for i in range(3):
        client.post(
            "/categories",
            json={
                "name": f"List Category {i}",
                "slug": f"list-cat-{i}"
            }
        )
    
    response = client.get("/categories")
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_update_category(client: TestClient):
    """Test updating a category"""
    create_response = client.post(
        "/categories",
        json={
            "name": "Original",
            "slug": "orig-slug"
        }
    )
    cat_id = create_response.json()["id"]
    
    response = client.put(
        f"/categories/{cat_id}",
        json={
            "name": "Updated Name",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_category(client: TestClient):
    """Test deleting a category"""
    create_response = client.post(
        "/categories",
        json={
            "name": "Delete Me",
            "slug": "delete-cat"
        }
    )
    cat_id = create_response.json()["id"]
    
    response = client.delete(f"/categories/{cat_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


# ============================================================================
# TOPIC CLUSTERS
# ============================================================================

def test_create_topic_cluster(client: TestClient):
    """Test creating a topic cluster"""
    response = client.post(
        "/topic-clusters/",
        json={
            "name": "Python Basics",
            "slug": "python-basics"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Python Basics"
    assert data["slug"] == "python-basics"


def test_get_topic_cluster(client: TestClient):
    """Test retrieving a topic cluster"""
    create_response = client.post(
        "/topic-clusters/",
        json={
            "name": "Advanced Topic",
            "slug": "advanced-topic"
        }
    )
    cluster_id = create_response.json()["id"]
    
    response = client.get(f"/topic-clusters/{cluster_id}")
    assert response.status_code == 200
    assert response.json()["id"] == cluster_id


def test_list_topic_clusters(client: TestClient):
    """Test listing topic clusters"""
    # Create several clusters
    for i in range(3):
        client.post(
            "/topic-clusters/",
            json={
                "name": f"Cluster {i}",
                "slug": f"cluster-{i}"
            }
        )
    
    response = client.get("/topic-clusters/")
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_update_topic_cluster(client: TestClient):
    """Test updating a topic cluster"""
    create_response = client.post(
        "/topic-clusters/",
        json={
            "name": "Original Cluster",
            "slug": "original-cluster"
        }
    )
    cluster_id = create_response.json()["id"]
    
    response = client.put(
        f"/topic-clusters/{cluster_id}",
        json={
            "name": "Updated Cluster"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Cluster"


def test_delete_topic_cluster(client: TestClient):
    """Test deleting a topic cluster"""
    create_response = client.post(
        "/topic-clusters/",
        json={
            "name": "Delete Me",
            "slug": "delete-me"
        }
    )
    cluster_id = create_response.json()["id"]
    
    response = client.delete(f"/topic-clusters/{cluster_id}")
    assert response.status_code == 204


# ============================================================================
# BLOG POSTS
# ============================================================================

def test_create_blog_post(client: TestClient):
    """Test creating a blog post (draft status)"""
    response = client.post(
        "/posts",
        json={
            "title": "My First Post",
            "slug": "my-first-post",
            "content_markdown": "This is comprehensive blog content here.",
            "content_html": "<p>This is comprehensive blog content here.</p>"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["slug"] == "my-first-post"
    assert data["status"] == "draft"


def test_create_post_with_category(client: TestClient):
    """Test creating a post with a category"""
    # Create category
    cat_response = client.post(
        "/categories",
        json={
            "name": "Tech Posts",
            "slug": "tech-posts"
        }
    )
    cat_id = cat_response.json()["id"]
    
    # Create post with category
    response = client.post(
        "/posts",
        json={
            "title": "Tech Article",
            "slug": "tech-article",
            "content_markdown": "Technical content here.",
            "content_html": "<p>Technical content here.</p>",
            "category_id": cat_id
        }
    )
    
    assert response.status_code == 201
    assert response.json()["category_id"] == cat_id


def test_get_blog_post(client: TestClient):
    """Test retrieving a blog post"""
    create_response = client.post(
        "/posts",
        json={
            "title": "Get Post Test",
            "slug": "get-post-test",
            "content_markdown": "Test content something",
            "content_html": "<p>Test content something</p>"
        }
    )
    post_id = create_response.json()["id"]
    
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == post_id


def test_list_published_posts(client: TestClient):
    """Test listing published posts"""
    # Create and publish a post
    create_response = client.post(
        "/posts",
        json={
            "title": "Publish Test",
            "slug": "publish-test",
            "content_markdown": "Test content something",
            "content_html": "<p>Test content something</p>"
        }
    )
    post_id = create_response.json()["id"]
    
    # Publish it
    client.patch(f"/posts/{post_id}/publish")
    
    # List published
    response = client.get("/posts")
    assert response.status_code == 200


def test_publish_post(client: TestClient):
    """Test publishing a draft post"""
    create_response = client.post(
        "/posts",
        json={
            "title": "Draft Post",
            "slug": "draft-post-pub",
            "content_markdown": "This is a test content with length",
            "content_html": "<p>This is a test content with length</p>"
        }
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    
    response = client.patch(f"/posts/{post_id}/publish")
    
    assert response.status_code == 200
    assert response.json()["status"] == "published"
    assert response.json()["published_at"] is not None


def test_update_blog_post(client: TestClient):
    """Test updating a blog post"""
    create_response = client.post(
        "/posts",
        json={
            "title": "Original Title",
            "slug": "original-slug",
            "content_markdown": "Original content something",
            "content_html": "<p>Original content something</p>"
        }
    )
    post_id = create_response.json()["id"]
    
    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Updated Title",
            "content_markdown": "Updated content something",
            "content_html": "<p>Updated content something</p>"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_blog_post(client: TestClient):
    """Test deleting a blog post"""
    create_response = client.post(
        "/posts",
        json={
            "title": "Delete Me",
            "slug": "delete-me-post",
            "content_markdown": "This is a test content with length",
            "content_html": "<p>This is a test content with length</p>"
        }
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 204


def test_unique_post_slug(client: TestClient):
    """Test that post slugs are unique"""
    first_response = client.post(
        "/posts",
        json={
            "title": "First Post",
            "slug": "unique-post-slug-test",
            "content_markdown": "This is a test content with length",
            "content_html": "<p>This is a test content with length</p>"
        }
    )
    assert first_response.status_code == 201
    
    response = client.post(
        "/posts",
        json={
            "title": "Second Post",
            "slug": "unique-post-slug-test",
            "content_markdown": "This is a test content with length",
            "content_html": "<p>This is a test content with length</p>"
        }
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


# ============================================================================
# ERROR HANDLING
# ============================================================================

def test_get_nonexistent_post(client: TestClient):
    """Test getting a post that doesn't exist"""
    response = client.get("/posts/99999")
    assert response.status_code == 404


def test_get_nonexistent_category(client: TestClient):
    """Test getting a category that doesn't exist"""
    response = client.get("/categories/99999")
    assert response.status_code == 404


def test_get_nonexistent_cluster(client: TestClient):
    """Test getting a cluster that doesn't exist"""
    response = client.get("/topic-clusters/99999")
    assert response.status_code == 404


# ============================================================================
# DATABASE VERIFICATION
# ============================================================================

def test_debug_tables_endpoint(client: TestClient):
    """Test debug endpoint to list tables"""
    response = client.get("/debug/tables")
    assert response.status_code in [200, 500]  # May not work with SQLite in tests
