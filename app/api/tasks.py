import logging
import json

from fastapi import UploadFile

from celery import shared_task
import asyncio

from .s3 import upload_service
from .email import send_email


async def process_files(video_file: UploadFile, image_file: UploadFile, email: str, task_id: str):
    response = upload_service.upload_video_file(image_file, video_file, "before/")
    convert_video.apply_async([response, email], task_id=task_id)


@shared_task
def convert_video(loc, email):
    '''
        todo: 모델 연동하는 부분
    '''

    logging.info(f"convert video done! {loc}")

    logging.info(f"email sent! {loc}")

    asyncio.run(send_email(email, json.dumps(loc)))

    return loc
