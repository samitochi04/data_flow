from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.topic_cluster_model import TopicCluster
from app.models.schemas.topic_cluster_schema import TopicClusterCreate, TopicClusterUpdate


class TopicClusterRepository:
    """
    Repository for TopicCluster database operations.
    Handles all async database queries related to topic clusters.
    """

    @staticmethod
    async def create(data: TopicClusterCreate, db: AsyncSession) -> TopicCluster:
        """
        Create a new topic cluster.
        
        Args:
            data: TopicClusterCreate schema with cluster details
            db: AsyncSession for database operations
            
        Returns:
            Created TopicCluster object
        """
        db_cluster = TopicCluster(
            name=data.name,
            slug=data.slug,
            pillar_post_id=data.pillar_post_id
        )
        db.add(db_cluster)
        await db.commit()
        await db.refresh(db_cluster)
        return db_cluster

    @staticmethod
    async def get_by_id(cluster_id: int, db: AsyncSession) -> Optional[TopicCluster]:
        """
        Get topic cluster by ID.
        
        Args:
            cluster_id: ID of cluster to retrieve
            db: AsyncSession for database operations
            
        Returns:
            TopicCluster object or None if not found
        """
        result = await db.execute(
            select(TopicCluster).where(TopicCluster.id == cluster_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_slug(slug: str, db: AsyncSession) -> Optional[TopicCluster]:
        """
        Get topic cluster by slug.
        
        Args:
            slug: Slug of cluster to retrieve
            db: AsyncSession for database operations
            
        Returns:
            TopicCluster object or None if not found
        """
        result = await db.execute(
            select(TopicCluster).where(TopicCluster.slug == slug)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
        """
        Get all topic clusters.
        
        Args:
            db: AsyncSession for database operations
            skip: Number of results to skip (pagination)
            limit: Maximum number of results to return
            
        Returns:
            List of TopicCluster objects
        """
        result = await db.execute(
            select(TopicCluster)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(cluster: TopicCluster, data: TopicClusterUpdate, db: AsyncSession) -> TopicCluster:
        """
        Update an existing topic cluster.
        
        Args:
            cluster: TopicCluster object to update
            data: TopicClusterUpdate schema with new values
            db: AsyncSession for database operations
            
        Returns:
            Updated TopicCluster object
        """
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cluster, key, value)

        db.add(cluster)
        await db.commit()
        await db.refresh(cluster)
        return cluster

    @staticmethod
    async def delete(cluster: TopicCluster, db: AsyncSession) -> None:
        """
        Delete a topic cluster.
        
        Args:
            cluster: TopicCluster object to delete
            db: AsyncSession for database operations
        """
        db.delete(cluster)
        await db.commit()

    @staticmethod
    async def slug_exists(slug: str, db: AsyncSession, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a slug already exists (excluding a specific cluster by ID).
        
        Args:
            slug: Slug to check
            db: AsyncSession for database operations
            exclude_id: Cluster ID to exclude from check (for updates)
            
        Returns:
            True if slug exists, False otherwise
        """
        query = select(TopicCluster).where(TopicCluster.slug == slug)
        if exclude_id:
            query = query.where(TopicCluster.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalars().first() is not None

    @staticmethod
    async def get_by_pillar_post(pillar_post_id: int, db: AsyncSession) -> Optional[TopicCluster]:
        """
        Get topic cluster by its pillar_post ID.
        
        Args:
            pillar_post_id: ID of the pillar post
            db: AsyncSession for database operations
            
        Returns:
            TopicCluster object or None if not found
        """
        result = await db.execute(
            select(TopicCluster).where(TopicCluster.pillar_post == pillar_post_id)
        )
        return result.scalars().first()
