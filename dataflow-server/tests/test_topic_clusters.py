import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.topic_cluster_schema import TopicClusterCreate, TopicClusterUpdate, TopicClusterOut
from app.repositories.topic_cluster_repository import TopicClusterRepository


# Create Tests
@pytest.mark.asyncio
async def test_create_topic_cluster(db_session: AsyncSession):
    """Test creating a new topic cluster."""
    data = TopicClusterCreate(
        name="Test Cluster",
        slug="test-cluster",
        pillar_post=None
    )
    
    cluster = await TopicClusterRepository.create(data, db_session)
    
    assert cluster.id is not None
    assert cluster.name == "Test Cluster"
    assert cluster.slug == "test-cluster"
    assert cluster.pillar_post is None
    assert cluster.created_at is not None
    assert cluster.updated_at is not None


@pytest.mark.asyncio
async def test_create_topic_cluster_with_pillar_post(db_session: AsyncSession):
    """Test creating a topic cluster with pillar_post reference."""
    data = TopicClusterCreate(
        name="Pillar Cluster",
        slug="pillar-cluster",
        pillar_post=1  # Reference to blog_posts.id = 1
    )
    
    cluster = await TopicClusterRepository.create(data, db_session)
    
    assert cluster.id is not None
    assert cluster.pillar_post == 1


@pytest.mark.asyncio
async def test_duplicate_topic_cluster_slug(db_session: AsyncSession):
    """Test that duplicate slugs are rejected."""
    data1 = TopicClusterCreate(
        name="First Cluster",
        slug="unique-slug",
        pillar_post=None
    )
    data2 = TopicClusterCreate(
        name="Second Cluster",
        slug="unique-slug",  # Same slug
        pillar_post=None
    )
    
    # Create first cluster
    await TopicClusterRepository.create(data1, db_session)
    
    # Check slug uniqueness
    slug_exists = await TopicClusterRepository.slug_exists("unique-slug", db_session)
    assert slug_exists is True


@pytest.mark.asyncio
async def test_slug_exists_false(db_session: AsyncSession):
    """Test slug_exists returns False for non-existent slug."""
    exists = await TopicClusterRepository.slug_exists("non-existent-slug", db_session)
    assert exists is False


# Read Tests
@pytest.mark.asyncio
async def test_get_topic_cluster_by_id(db_session: AsyncSession):
    """Test retrieving a topic cluster by ID."""
    data = TopicClusterCreate(
        name="Get Test",
        slug="get-test",
        pillar_post=None
    )
    
    created = await TopicClusterRepository.create(data, db_session)
    retrieved = await TopicClusterRepository.get_by_id(created.id, db_session)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Get Test"
    assert retrieved.slug == "get-test"


@pytest.mark.asyncio
async def test_get_topic_cluster_by_slug(db_session: AsyncSession):
    """Test retrieving a topic cluster by slug."""
    data = TopicClusterCreate(
        name="Slug Test",
        slug="slug-test",
        pillar_post=None
    )
    
    await TopicClusterRepository.create(data, db_session)
    retrieved = await TopicClusterRepository.get_by_slug("slug-test", db_session)
    
    assert retrieved is not None
    assert retrieved.name == "Slug Test"
    assert retrieved.slug == "slug-test"


@pytest.mark.asyncio
async def test_get_nonexistent_topic_cluster(db_session: AsyncSession):
    """Test retrieving non-existent topic cluster returns None."""
    result = await TopicClusterRepository.get_by_id(999999, db_session)
    assert result is None


@pytest.mark.asyncio
async def test_list_topic_clusters(db_session: AsyncSession):
    """Test listing topic clusters."""
    # Create test clusters
    clusters_data = [
        TopicClusterCreate(name="Cluster 1", slug="cluster-1", pillar_post=None),
        TopicClusterCreate(name="Cluster 2", slug="cluster-2", pillar_post=None),
        TopicClusterCreate(name="Cluster 3", slug="cluster-3", pillar_post=None),
    ]
    
    for data in clusters_data:
        await TopicClusterRepository.create(data, db_session)
    
    clusters = await TopicClusterRepository.get_all(db_session, skip=0, limit=100)
    
    assert len(clusters) >= 3


@pytest.mark.asyncio
async def test_list_topic_clusters_pagination(db_session: AsyncSession):
    """Test pagination in listing topic clusters."""
    # Create test clusters
    for i in range(5):
        data = TopicClusterCreate(
            name=f"Cluster {i}",
            slug=f"cluster-{i}",
            pillar_post=None
        )
        await TopicClusterRepository.create(data, db_session)
    
    # Test skip and limit
    page1 = await TopicClusterRepository.get_all(db_session, skip=0, limit=2)
    page2 = await TopicClusterRepository.get_all(db_session, skip=2, limit=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


# Update Tests
@pytest.mark.asyncio
async def test_update_topic_cluster(db_session: AsyncSession):
    """Test updating a topic cluster."""
    # Create initial cluster
    data = TopicClusterCreate(
        name="Original Name",
        slug="original-slug",
        pillar_post=None
    )
    cluster = await TopicClusterRepository.create(data, db_session)
    
    # Update cluster
    update_data = TopicClusterUpdate(
        name="Updated Name",
        slug="updated-slug",
        pillar_post=2
    )
    updated = await TopicClusterRepository.update(cluster, update_data, db_session)
    
    assert updated.name == "Updated Name"
    assert updated.slug == "updated-slug"
    assert updated.pillar_post == 2


@pytest.mark.asyncio
async def test_update_topic_cluster_partial(db_session: AsyncSession):
    """Test partial update of a topic cluster."""
    # Create initial cluster
    data = TopicClusterCreate(
        name="Original",
        slug="original",
        pillar_post=None
    )
    cluster = await TopicClusterRepository.create(data, db_session)
    
    # Partial update (only name)
    update_data = TopicClusterUpdate(name="New Name")
    updated = await TopicClusterRepository.update(cluster, update_data, db_session)
    
    assert updated.name == "New Name"
    assert updated.slug == "original"  # Unchanged


# Delete Tests
@pytest.mark.asyncio
async def test_delete_topic_cluster(db_session: AsyncSession):
    """Test deleting a topic cluster."""
    # Create cluster
    data = TopicClusterCreate(
        name="Delete Test",
        slug="delete-test",
        pillar_post=None
    )
    cluster = await TopicClusterRepository.create(data, db_session)
    cluster_id = cluster.id
    
    # Delete cluster
    await TopicClusterRepository.delete(cluster, db_session)
    
    # Verify deletion
    retrieved = await TopicClusterRepository.get_by_id(cluster_id, db_session)
    assert retrieved is None


# Pydantic Schema Tests
@pytest.mark.asyncio
async def test_topic_cluster_schema_validation(db_session: AsyncSession):
    """Test Pydantic schema validation."""
    data = TopicClusterCreate(
        name="Schema Test",
        slug="schema-test",
        pillar_post=None
    )
    
    cluster = await TopicClusterRepository.create(data, db_session)
    output = TopicClusterOut.model_validate(cluster)
    
    assert output.id is not None
    assert output.name == "Schema Test"
    assert output.slug == "schema-test"
    assert output.created_at is not None
    assert output.updated_at is not None


# Integration Tests
@pytest.mark.asyncio
async def test_full_topic_cluster_lifecycle(db_session: AsyncSession):
    """Test complete topic cluster lifecycle."""
    # Create
    create_data = TopicClusterCreate(
        name="Lifecycle Test",
        slug="lifecycle-test",
        pillar_post=None
    )
    cluster = await TopicClusterRepository.create(create_data, db_session)
    assert cluster.id is not None
    
    # Read
    retrieved = await TopicClusterRepository.get_by_id(cluster.id, db_session)
    assert retrieved.name == "Lifecycle Test"
    
    # Update
    update_data = TopicClusterUpdate(
        name="Lifecycle Updated",
        pillar_post=1
    )
    updated = await TopicClusterRepository.update(cluster, update_data, db_session)
    assert updated.name == "Lifecycle Updated"
    assert updated.pillar_post == 1
    
    # Delete
    await TopicClusterRepository.delete(updated, db_session)
    final = await TopicClusterRepository.get_by_id(cluster.id, db_session)
    assert final is None


# Foreign Key Tests
@pytest.mark.asyncio
async def test_get_topic_clusters_by_pillar_post(db_session: AsyncSession):
    """Test retrieving topic clusters by pillar_post."""
    # Create clusters with same pillar_post
    data1 = TopicClusterCreate(name="Cluster A", slug="cluster-a", pillar_post=5)
    data2 = TopicClusterCreate(name="Cluster B", slug="cluster-b", pillar_post=5)
    data3 = TopicClusterCreate(name="Cluster C", slug="cluster-c", pillar_post=6)
    
    await TopicClusterRepository.create(data1, db_session)
    await TopicClusterRepository.create(data2, db_session)
    await TopicClusterRepository.create(data3, db_session)
    
    clusters = await TopicClusterRepository.get_by_pillar_post(5, db_session)
    
    assert len(clusters) == 2
    assert all(c.pillar_post == 5 for c in clusters)
