import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from celery import Celery
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import config
from app.api.api import api_router
from app.api.tasks import delete_files


def create_app():
    current_app = FastAPI(title="API server of project HIDE",
                          description="Mosaic your video",
                          docs_url='/api/docs',
                          redoc_url='/api/redoc',
                          openapi_url='/api/openapi.json',
                          version="1.0.0")

    current_app.include_router(api_router, prefix="/api")

    logging.info("app created!")

    return current_app


app = create_app()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


celery = Celery(
    __name__,
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}"
)

celery.conf.imports = [
    'app.api.tasks',
]
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serialize='json',
    timezone='Asia/Seoul',
    enable_utc=True
)

scheduler = BackgroundScheduler(timezone='Asia/Seoul')
scheduler.add_job(delete_files, 'cron', hour="0", minute="0", second="0")
scheduler.start()

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="example.log", filemode="w", level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)


if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)
