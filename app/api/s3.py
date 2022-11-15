import logging
from fastapi import UploadFile

import boto3
from botocore.exceptions import ClientError

from app.config import AWS_SECRET_KEY, AWS_ACCESS_KEY_ID

class UploadService:
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.bucket_name = "hide-file"
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )


    def upload_video_file(self, image_file: UploadFile, video_file: UploadFile, dir_name):
        response = {
            "video_loc": dir_name + video_file.filename,
            "image_loc": dir_name + image_file.filename
        }

        try:
            self.s3_client.upload_fileobj(
                video_file.file,
                self.bucket_name,
                response["video_loc"]
            )
            self.s3_client.upload_fileobj(
                image_file.file,
                self.bucket_name,
                response["image_loc"]
            )
        except ClientError as e:
            logging.error(e)
        except Exception as e:
            logging.error("There was an error uploading the file")

        return response


upload_service = UploadService(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
