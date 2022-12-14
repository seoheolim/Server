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
from models.process import mosaic
from .s3 import s3_service
from .email import send_email
from .audio import extract_audio, combine_audio


async def process_files(video_file: UploadFile, image_file: UploadFile, email: str, option: str, task_id: str):

    video_path, video_name = await save_file(video_file, task_id)
    image_path, _ = await save_file(image_file, task_id)
    convert_video.apply_async(args=[image_path, video_path, video_name, email, option], task_id=task_id, expires=30)


async def generate_task_id(email: str):
    rand_str = ""
    for i in range(5):
        rand_str += str(random.choice(string.ascii_letters + string.digits))
    rand_str += email.replace('.com', "")

    return rand_str


async def save_file(file: UploadFile, task_id: str):
    new_file_name = f"{task_id}{file.filename}"
    path = "temp/" + new_file_name

    with open(path, "wb") as f:
        f.write(file.file.read())

    logging.info(f"file saved! [{new_file_name}]")

    return path, new_file_name


@shared_task()
def convert_video(image_path, video_path, entire_video_name, email, option):

    video_name = entire_video_name.split(".")[0]

    logging.info(f"image_path: {image_path}, video_path: {video_path}")
    audio_path = extract_audio(video_path, video_name)

    logging.info(f"audio extract done! -> {audio_path}")

    # 모델 연동하는 부분
    converted_video_path = mosaic(video_path, image_path, video_name, option)
    temp_path = ""

    # 음성 파일과 영상 파일 합치기
    if audio_path is not None:
        temp_path = converted_video_path
        converted_video_path = combine_audio(converted_video_path, entire_video_name, audio_path)

    logging.info(f"converted_video_path: {converted_video_path}")

    # 변환된 영상 S3 업로드
    s3_service.upload_video_file(converted_video_path, entire_video_name)

    # 업로드 완료 후, 이메일 전송
    asyncio.run(send_email(email, entire_video_name))
    logging.info(f"email sent -> {email}")

    # 임시 파일 삭제
    os.remove(image_path)
    if audio_path is not None:
        os.remove(temp_path)
        os.remove(audio_path)

    os.remove(video_path)
    os.remove(converted_video_path)

    logging.info(f"deleted, {image_path}, {audio_path}, {video_path}, {converted_video_path}, {temp_path}")
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
