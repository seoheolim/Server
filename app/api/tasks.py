import logging
import json
import os

from fastapi import UploadFile

from celery import shared_task
import asyncio

from .s3 import upload_service
from .email import send_email
from .audio import extract_audio, combine_audio


async def process_files(video_file: UploadFile, image_file: UploadFile, email: str, task_id: str):

    video_path, video_name = save_file(video_file)
    image_path, image_name = save_file(image_file)
    convert_video.apply_async([image_path, video_path, video_name, email], task_id=task_id)


def save_file(file: UploadFile):
    path = f"app/api/temp/{file.filename}"
    with open(path, "wb") as f:
        f.write(file.file.read())

    return path, file.filename


@shared_task
def convert_video(image_path, video_path, entire_video_name, email):

    video_name = entire_video_name.split(".")[0]
    audio_path = extract_audio(video_path, video_name)

    logging.info(f"audio extract done! -> {audio_path}")
    '''
        todo1: 모델 연동하는 부분
    '''

    # 음성 파일과 영상 파일 합치기
    if audio_path is not None:
        combine_audio(video_path, audio_path)

    logging.info(f"video_path: {video_path}")

    # 변환된 영상 S3 업로드
    upload_service.upload_video_file(video_path, entire_video_name)

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
