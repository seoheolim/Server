import logging

from fastapi import APIRouter, UploadFile, BackgroundTasks

from app.api.tasks import process_files, convert_video

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.post("/upload")
async def upload_files(image: UploadFile, video: UploadFile, email: str, back_grond_task: BackgroundTasks):
    logging.info("upload_file start")
    back_grond_task.add_task(process_files, video, image, email, "test")
    return {"message": "start!"}


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    logging.info("task status")
    result = convert_video.AsyncResult(task_id)
    return {"message": result.info}
