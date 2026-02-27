from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.topic_cluster_schema import TopicClusterCreate, TopicClusterUpdate, TopicClusterOut
from app.services.topic_cluster_service import TopicClusterService


class TopicClusterController:
    """
    Controller for topic cluster HTTP operations.
    Bridges HTTP layer to service layer.
    """

    @staticmethod
    async def create_topic_cluster(
        data: TopicClusterCreate,
        db: AsyncSession = Depends(get_db)
    ) -> TopicClusterOut:
        """
        Create a new topic cluster.
        
        Args:
            data: TopicClusterCreate schema
            db: Database session dependency
            
        Returns:
            TopicClusterOut with created cluster details
        """
        return await TopicClusterService.create_topic_cluster(data, db)

    @staticmethod
    async def get_topic_cluster(
        cluster_id: int,
        db: AsyncSession = Depends(get_db)
    ) -> TopicClusterOut:
        """
        Get a specific topic cluster by ID.
        
        Args:
            cluster_id: ID of the cluster
            db: Database session dependency
            
        Returns:
            TopicClusterOut with cluster details
        """
        return await TopicClusterService.get_topic_cluster(cluster_id, db)

    @staticmethod
    async def get_topic_cluster_by_slug(
        slug: str,
        db: AsyncSession = Depends(get_db)
    ) -> TopicClusterOut:
        """
        Get a topic cluster by slug.
        
        Args:
            slug: Slug of the cluster
            db: Database session dependency
            
        Returns:
            TopicClusterOut with cluster details
            
        Raises:
            HTTPException: If cluster not found
        """
        from app.repositories.topic_cluster_repository import TopicClusterRepository
        
        cluster = await TopicClusterRepository.get_by_slug(slug, db)
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic cluster with slug '{slug}' not found"
            )
        return TopicClusterOut.model_validate(cluster)

    @staticmethod
    async def list_topic_clusters(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
    ) -> list:
        """
        List all topic clusters with pagination.
        
        Args:
            skip: Number of results to skip
            limit: Maximum number of results
            db: Database session dependency
            
        Returns:
            List of TopicClusterOut schemas
        """
        return await TopicClusterService.list_topic_clusters(db, skip, limit)

    @staticmethod
    async def update_topic_cluster(
        cluster_id: int,
        data: TopicClusterUpdate,
        db: AsyncSession = Depends(get_db)
    ) -> TopicClusterOut:
        """
        Update an existing topic cluster.
        
        Args:
            cluster_id: ID of cluster to update
            data: TopicClusterUpdate schema with new values
            db: Database session dependency
            
        Returns:
            TopicClusterOut with updated cluster details
        """
        return await TopicClusterService.update_topic_cluster(cluster_id, data, db)

    @staticmethod
    async def delete_topic_cluster(
        cluster_id: int,
        db: AsyncSession = Depends(get_db)
    ) -> dict:
        """
        Delete a topic cluster.
        
        Args:
            cluster_id: ID of cluster to delete
            db: Database session dependency
            
        Returns:
            Dictionary with deletion confirmation message
        """
        return await TopicClusterService.delete_topic_cluster(cluster_id, db)
