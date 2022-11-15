import logging

from fastapi import APIRouter, UploadFile, BackgroundTasks

from app.api.tasks import process_files, convert_video

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.get("/greeting")
async def greeting():
    return "hi"


@router.post("/upload")
async def upload_files(image: UploadFile, video: UploadFile, task_id: str):
    await process_files(video, image, task_id)
    return {"message": "start!"}


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    logging.info("TEST")
    result = convert_video.AsyncResult(task_id)
    return {"message": result.info}
