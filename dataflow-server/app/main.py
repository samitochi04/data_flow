from app.models.db.user_model import User

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends
from scalar_fastapi import get_scalar_api_reference
from app.core.database import engine, Base, get_db

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Import routes
from app.api.routes.user_routes import router as user_router

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

# Access Database
router = APIRouter(prefix="/debug")

@router.get("/tables")
async def list_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    ))
    return result.fetchall()

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
