import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.users.routers import router as users_router
from app.tasks.routers import router as tasks_router



def init_db():
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="FastAPI Modular App",
    description="FastAPI application with modular architecture",
    version="0.1.0",
)

# sCORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
async def root():
    return {"message": "API is running"}


if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)