from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.controllers.topic_cluster_controller import TopicClusterController
from app.core.database import get_db
from app.models.schemas.topic_cluster_schema import TopicClusterCreate, TopicClusterUpdate, TopicClusterOut

router = APIRouter(prefix="/topic-clusters", tags=["Topic Clusters"])


@router.post("/", response_model=TopicClusterOut, status_code=status.HTTP_201_CREATED)
async def create_topic_cluster(
    data: TopicClusterCreate,
    db: AsyncSession = Depends(get_db)
) -> TopicClusterOut:
    """
    Create a new topic cluster.
    
    Returns:
        - **201**: Topic cluster created successfully
        - **400**: Slug already exists or invalid data
        - **500**: Internal server error
    """
    return await TopicClusterController.create_topic_cluster(data, db)


@router.get("/", response_model=list[TopicClusterOut])
async def list_topic_clusters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
) -> list:
    """
    List all topic clusters with pagination.
    
    Query Parameters:
        - **skip**: Number of records to skip (default: 0)
        - **limit**: Maximum number of records (default: 100, max: 1000)
    
    Returns:
        - **200**: List of topic clusters
        - **500**: Internal server error
    """
    return await TopicClusterController.list_topic_clusters(skip, limit, db)


@router.get("/{cluster_id}", response_model=TopicClusterOut)
async def get_topic_cluster(
    cluster_id: int,
    db: AsyncSession = Depends(get_db)
) -> TopicClusterOut:
    """
    Get a specific topic cluster by ID.
    
    Path Parameters:
        - **cluster_id**: ID of the topic cluster
    
    Returns:
        - **200**: Topic cluster details
        - **404**: Cluster not found
        - **500**: Internal server error
    """
    return await TopicClusterController.get_topic_cluster(cluster_id, db)


@router.get("/slug/{slug}", response_model=TopicClusterOut)
async def get_topic_cluster_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> TopicClusterOut:
    """
    Get a topic cluster by its slug.
    
    Path Parameters:
        - **slug**: URL-friendly slug of the topic cluster
    
    Returns:
        - **200**: Topic cluster details
        - **404**: Cluster not found
        - **500**: Internal server error
    """
    return await TopicClusterController.get_topic_cluster_by_slug(slug, db)


@router.put("/{cluster_id}", response_model=TopicClusterOut)
async def update_topic_cluster(
    cluster_id: int,
    data: TopicClusterUpdate,
    db: AsyncSession = Depends(get_db)
) -> TopicClusterOut:
    """
    Update a topic cluster.
    
    Path Parameters:
        - **cluster_id**: ID of the topic cluster
    
    Request Body:
        - **name**: Topic cluster name (optional)
        - **slug**: URL-friendly slug (optional, must be unique)
        - **pillar_post**: ID of the pillar blog post (optional, nullable)
    
    Returns:
        - **200**: Updated topic cluster details
        - **404**: Cluster not found
        - **400**: Invalid data or duplicate slug
        - **500**: Internal server error
    """
    return await TopicClusterController.update_topic_cluster(cluster_id, data, db)


@router.delete("/{cluster_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic_cluster(
    cluster_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a topic cluster.
    
    Path Parameters:
        - **cluster_id**: ID of the topic cluster
    
    Returns:
        - **204**: Cluster deleted successfully (no content)
        - **404**: Cluster not found
        - **500**: Internal server error
    """
    await TopicClusterController.delete_topic_cluster(cluster_id, db)
