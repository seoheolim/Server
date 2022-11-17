import logging
import random
import os
import string
import datetime
import asyncio
import json

from fastapi import UploadFile
from celery import shared_task

from app.db.redis import redis_db
from .s3 import s3_service
from .email import send_email
from .audio import extract_audio, combine_audio


async def process_files(video_file: UploadFile, image_file: UploadFile, email: str, task_id: str):

    video_path, video_name = save_file(video_file, task_id)
    image_path, _ = save_file(image_file, task_id)
    convert_video.apply_async(args=[image_path, video_path, video_name, email], task_id=task_id, expires=30)


async def generate_task_id(email: str):
    rand_str = ""
    for i in range(5):
        rand_str += str(random.choice(string.ascii_letters + string.digits))
    rand_str += email.replace('.com', "")

    return rand_str


def save_file(file: UploadFile, task_id: str):
    new_file_name = f"{task_id}{file.filename}"
    path = "app/api/temp/" + new_file_name
    with open(path, "wb") as f:
        f.write(file.file.read())

    return path, new_file_name


@shared_task()
def convert_video(image_path, video_path, entire_video_name, email):

    video_name = entire_video_name.split(".")[0]
    audio_path = extract_audio(video_path, video_name)

    logging.info(f"audio extract done! -> {audio_path}")

    '''
        todo: 모델 연동하는 부분
    '''

    # 음성 파일과 영상 파일 합치기
    if audio_path is not None:
        combine_audio(video_path, audio_path)

    logging.info(f"video_path: {video_path}")

    # 변환된 영상 S3 업로드
    s3_service.upload_video_file(video_path, entire_video_name)

    # 업로드 완료 후, 이메일 전송
    asyncio.run(send_email(email, entire_video_name))
    logging.info(f"email sent -> {email}")

    # 임시 파일 삭제
    os.remove(image_path)
    if audio_path is not None:
        os.remove(audio_path)
    os.remove(video_path)
    logging.info(f"deleted, {image_path}, {audio_path}, {video_path}")
    return {"message": "[convert_video] done!"}


def delete_files():
    target = {
        "Objects": []
    }
    criteria = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    keys = redis_db.keys("LOG*@*")

    for key in keys:
        value = json.loads(redis_db.get(key))
        if value["exp"] is False and value["saved_time"] > criteria:
            target["Objects"].append({"Key": value["video_path"]})
            value["exp"] = True
            value = json.dumps(value)
            redis_db.set(key, value)

    logging.info(f"[delete_files()]: target={target}")
    if len(target["Objects"]) > 0:
        s3_service.delete_video_files(target)
