from fastapi import FastAPI
from app.routers.tasks import router

app = FastAPI()

app.include_router(router)
