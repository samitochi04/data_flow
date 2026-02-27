"""Tests for Category model and endpoints"""

from fastapi.testclient import TestClient


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
    assert data["description"] == "Articles about web development"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_subcategory(client: TestClient):
    """Test creating a subcategory under a parent category"""
    # Create parent category
    parent_response = client.post(
        "/categories",
        json={
            "name": "Web Development",
            "slug": "web-development",
            "description": "Parent category"
        }
    )
    assert parent_response.status_code == 201
    parent_id = parent_response.json()["id"]
    
    # Create subcategory
    response = client.post(
        "/categories",
        json={
            "name": "Frontend",
            "slug": "frontend",
            "description": "Frontend development",
            "parent_id": parent_id
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Frontend"
    assert data["parent_id"] == parent_id


def test_duplicate_slug_rejected(client: TestClient):
    """Test that duplicate slugs are rejected"""
    # Create first category
    client.post(
        "/categories",
        json={
            "name": "Web Development",
            "slug": "web-dev",
            "description": "First category"
        }
    )
    
    # Try to create second with same slug
    response = client.post(
        "/categories",
        json={
            "name": "Different Name",
            "slug": "web-dev",
            "description": "Different category"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_category(client: TestClient):
    """Test retrieving a category by ID"""
    # Create category
    create_response = client.post(
        "/categories",
        json={
            "name": "Python",
            "slug": "python",
            "description": "Python programming"
        }
    )
    category_id = create_response.json()["id"]
    
    # Get category
    response = client.get(f"/categories/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Python"
    assert data["slug"] == "python"


def test_get_nonexistent_category(client: TestClient):
    """Test getting a category that doesn't exist"""
    response = client.get("/categories/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_categories(client: TestClient):
    """Test listing all top-level categories"""
    # Create multiple categories
    for i in range(3):
        client.post(
            "/categories",
            json={
                "name": f"Category {i}",
                "slug": f"category-{i}",
                "description": f"Description {i}"
            }
        )
    
    # List categories
    response = client.get("/categories")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_list_categories_with_pagination(client: TestClient):
    """Test pagination in category listing"""
    # Create 5 categories
    for i in range(5):
        client.post(
            "/categories",
            json={
                "name": f"Category {i}",
                "slug": f"category-{i}",
            }
        )
    
    # Test with limit
    response = client.get("/categories?limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_list_categories_tree(client: TestClient):
    """Test listing categories in hierarchical tree structure"""
    # Create parent
    parent_response = client.post(
        "/categories",
        json={
            "name": "Web Development",
            "slug": "web-dev",
        }
    )
    parent_id = parent_response.json()["id"]
    
    # Create children
    for i in range(2):
        client.post(
            "/categories",
            json={
                "name": f"Subcategory {i}",
                "slug": f"subcategory-{i}",
                "parent_id": parent_id
            }
        )
    
    # Get tree
    response = client.get("/categories/tree")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_category_tree(client: TestClient):
    """Test getting a category with its children"""
    # Create parent
    parent_response = client.post(
        "/categories",
        json={
            "name": "Backend",
            "slug": "backend",
        }
    )
    parent_id = parent_response.json()["id"]
    
    # Create child
    client.post(
        "/categories",
        json={
            "name": "Python",
            "slug": "python",
            "parent_id": parent_id
        }
    )
    
    # Get tree for parent
    response = client.get(f"/categories/{parent_id}/tree")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == parent_id
    assert "children" in data
    assert len(data["children"]) > 0


def test_update_category(client: TestClient):
    """Test updating a category"""
    # Create category
    create_response = client.post(
        "/categories",
        json={
            "name": "Original Name",
            "slug": "original-slug",
            "description": "Original description"
        }
    )
    category_id = create_response.json()["id"]
    
    # Update category
    response = client.put(
        f"/categories/{category_id}",
        json={
            "name": "Updated Name",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"
    assert data["slug"] == "original-slug"  # Slug unchanged


def test_update_category_slug(client: TestClient):
    """Test updating just the slug of a category"""
    # Create category
    create_response = client.post(
        "/categories",
        json={
            "name": "Category",
            "slug": "original-slug",
        }
    )
    category_id = create_response.json()["id"]
    
    # Update slug
    response = client.put(
        f"/categories/{category_id}",
        json={"slug": "new-slug"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "new-slug"


def test_delete_category(client: TestClient):
    """Test deleting a category"""
    # Create category
    create_response = client.post(
        "/categories",
        json={
            "name": "To Delete",
            "slug": "to-delete",
        }
    )
    category_id = create_response.json()["id"]
    
    # Delete category
    response = client.delete(f"/categories/{category_id}")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 404


def test_delete_category_with_children_fails(client: TestClient):
    """Test that deleting a category with children fails"""
    # Create parent
    parent_response = client.post(
        "/categories",
        json={
            "name": "Parent",
            "slug": "parent",
        }
    )
    parent_id = parent_response.json()["id"]
    
    # Create child
    client.post(
        "/categories",
        json={
            "name": "Child",
            "slug": "child",
            "parent_id": parent_id
        }
    )
    
    # Try to delete parent
    response = client.delete(f"/categories/{parent_id}")
    
    assert response.status_code == 400
    assert "Cannot delete category with" in response.json()["detail"]


def test_create_category_with_nonexistent_parent(client: TestClient):
    """Test creating a category with a non-existent parent fails"""
    response = client.post(
        "/categories",
        json={
            "name": "Orphan",
            "slug": "orphan",
            "parent_id": 99999
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_minimal_category_creation(client: TestClient):
    """Test creating a category with only required fields"""
    response = client.post(
        "/categories",
        json={
            "name": "DevOps",
            "slug": "devops"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "DevOps"
    assert data["slug"] == "devops"
    assert data["description"] is None
    assert data["parent_id"] is None
