from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.topic_cluster_schema import TopicClusterCreate, TopicClusterUpdate, TopicClusterOut
from app.repositories.topic_cluster_repository import TopicClusterRepository


class TopicClusterService:
    """
    Service layer for topic cluster business logic.
    Handles validation, authorization, and orchestration.
    """

    @staticmethod
    async def create_topic_cluster(data: TopicClusterCreate, db: AsyncSession) -> TopicClusterOut:
        """
        Create a new topic cluster with validation.
        
        Args:
            data: TopicClusterCreate schema with cluster details
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If slug already exists
            
        Returns:
            TopicClusterOut schema with created cluster data
        """
        # Check if slug already exists
        if await TopicClusterRepository.slug_exists(data.slug, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{data.slug}' already exists"
            )

        try:
            cluster = await TopicClusterRepository.create(data, db)
            return TopicClusterOut.model_validate(cluster)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create topic cluster: {str(e)}"
            )

    @staticmethod
    async def get_topic_cluster(cluster_id: int, db: AsyncSession) -> TopicClusterOut:
        """
        Get topic cluster by ID.
        
        Raises:
            HTTPException: If cluster not found
            
        Returns:
            TopicClusterOut schema with cluster data
        """
        cluster = await TopicClusterRepository.get_by_id(cluster_id, db)
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic cluster with ID {cluster_id} not found"
            )
        return TopicClusterOut.model_validate(cluster)

    @staticmethod
    async def list_topic_clusters(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
        """
        List all topic clusters.
        
        Args:
            db: AsyncSession for database operations
            skip: Number of results to skip (pagination)
            limit: Maximum number of results
            
        Returns:
            List of TopicClusterOut schemas
        """
        clusters = await TopicClusterRepository.get_all(db, skip, limit)
        return [TopicClusterOut.model_validate(cluster) for cluster in clusters]

    @staticmethod
    async def update_topic_cluster(
        cluster_id: int,
        data: TopicClusterUpdate,
        db: AsyncSession
    ) -> TopicClusterOut:
        """
        Update an existing topic cluster.
        
        Args:
            cluster_id: ID of cluster to update
            data: TopicClusterUpdate schema with new values
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If cluster not found or slug exists
            
        Returns:
            TopicClusterOut schema with updated cluster data
        """
        cluster = await TopicClusterRepository.get_by_id(cluster_id, db)
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic cluster with ID {cluster_id} not found"
            )

        # Check if new slug already exists (if being changed)
        if data.slug and data.slug != cluster.slug:
            if await TopicClusterRepository.slug_exists(data.slug, db, exclude_id=cluster_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slug '{data.slug}' already exists"
                )

        try:
            updated_cluster = await TopicClusterRepository.update(cluster, data, db)
            return TopicClusterOut.model_validate(updated_cluster)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update topic cluster: {str(e)}"
            )

    @staticmethod
    async def delete_topic_cluster(cluster_id: int, db: AsyncSession) -> dict:
        """
        Delete a topic cluster.
        
        Args:
            cluster_id: ID of cluster to delete
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If cluster not found
            
        Returns:
            Dictionary with deletion message
        """
        cluster = await TopicClusterRepository.get_by_id(cluster_id, db)
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic cluster with ID {cluster_id} not found"
            )

        try:
            await TopicClusterRepository.delete(cluster, db)
            return {"message": f"Topic cluster '{cluster.name}' deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete topic cluster: {str(e)}"
            )
