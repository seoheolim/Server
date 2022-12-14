import logging

from fastapi import APIRouter, UploadFile, BackgroundTasks, Form

from app.api.tasks import process_files, convert_video, generate_task_id

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.post("/upload")
async def upload_files(image: UploadFile, video: UploadFile, back_grond_task: BackgroundTasks, option: str = Form(), email: str = Form()):
    logging.info("upload_file start")
    task_id = await generate_task_id(email)
    back_grond_task.add_task(process_files, video, image, email, option, task_id)
    return {"message": "start!"}


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    logging.info("task status")
    result = convert_video.AsyncResult(task_id)
    return {"message": result.info}


import socket
@router.get("/")
async def root():
    return f"Container ID: {socket.gethostname()}"
