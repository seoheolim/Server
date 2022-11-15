import logging
from fastapi import UploadFile

from celery import shared_task

from .s3 import upload_service


async def process_files(video_file: UploadFile, image_file: UploadFile, task_id):
    response = upload_service.upload_video_file(image_file, video_file, "before/")
    convert_video.apply_async([response], task_id=task_id)


@shared_task
def convert_video(loc):
    import time
    time.sleep(5)
    # todo
    print("done!")
    logging.info(f"convert video done! {loc}")
    return loc


