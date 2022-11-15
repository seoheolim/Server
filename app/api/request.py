import logging

from fastapi import APIRouter, UploadFile, BackgroundTasks

from app.api.tasks import process_files

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.get("/greeting")
async def greeting():
    return "hi"


@router.post("/upload")
async def upload_files(image: UploadFile, video: UploadFile):
    # back_ground_tasks.add_task(process_files, image, video)
    await process_files(video, image)
    return {"message": "start!"}


#
#
# @router.get("/task/{task_id}")
# async def get_task_status(task_id: str):
#     return divide.AsyncResult(task_id)
