import logging

import uvicorn
from fastapi import FastAPI
from celery import Celery

from app import config
from app.api.api import api_router

logging.basicConfig(level=logging.INFO)


def create_app():
    current_app = FastAPI(title="API server of project HIDE",
                          description="Mosaic your video",
                          version="1.0.0")

    current_app.include_router(api_router, prefix="/api")

    logging.info("app created!")

    return current_app


app = create_app()

celery = Celery(
    __name__,
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}"
)

celery.conf.imports = [
    'app.api.tasks',
]

if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)
