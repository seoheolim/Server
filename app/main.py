import logging

import uvicorn
from fastapi import FastAPI

from api.api import api_router

logging.basicConfig(level=logging.INFO)


def create_app():
    current_app = FastAPI(title="API server of project HIDE",
                          description="Mosaic your video",
                          version="1.0.0")

    current_app.include_router(api_router, prefix="/api")
    logging.info("app created!")

    return current_app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)
