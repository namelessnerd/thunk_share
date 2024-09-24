from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.creatives import router as creatives_router
from data.utils.logging.config import setup_logging

setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers
app.include_router(creatives_router, prefix="/creatives", tags=["Creatives"])


@app.get("/")
async def root():
    return {"message": "Welcome to the API"}
