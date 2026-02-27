from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends
from scalar_fastapi import get_scalar_api_reference
from app.core.database import engine, Base, get_db

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession

# Import all models to register them with SQLAlchemy
from app.models.db import base  # noqa: F401

# Import routes
from app.api.routes.user_routes import router as user_router
from app.api.routes.category_routes import router as category_router
from app.api.routes.topic_cluster_routes import router as topic_cluster_router
from app.api.routes.blog_post_routes import router as blog_post_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    print("App starting... creating tables")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # --- shutdown ---
    print("App shutting down...")


app = FastAPI(title="Data Flow API", lifespan=lifespan)

# Include routes
app.include_router(user_router)
app.include_router(category_router)
app.include_router(topic_cluster_router)
app.include_router(blog_post_router)

# Access Database
router = APIRouter(prefix="/debug")

@router.get("/tables")
async def list_tables(db: AsyncSession = Depends(get_db)):
    """List all tables in the database (SQLite and PostgreSQL compatible)"""
    async with engine.connect() as conn:
        def get_table_names(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        
        table_names = await conn.run_sync(get_table_names)
        return {"tables": table_names}

app.include_router(router)

@app.get("/")
def entry():
    return '<h2 style="background-color: dda15e; color: 001219;">Welcome to Data Flow API</h2>'

@app.get("/health")
def health():
    return {
        "status": "Ok"
    }

# Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)
