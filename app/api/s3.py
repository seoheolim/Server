import logging

import boto3
from botocore.exceptions import ClientError

from app.config.config import AWS_SECRET_KEY, AWS_ACCESS_KEY_ID


class S3Service:
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.bucket_name = "hide-file"
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def upload_video_file(self, video_path: str, video_name: str):
        try:
            with open(video_path, "rb") as f:
                self.s3_client.upload_fileobj(f, self.bucket_name, "result/" + video_name)
        except ClientError as e:
            logging.error(e)
        except Exception as e:
            logging.error(f"There was an error uploading the file, {e}")
        return

    def delete_video_files(self, to_be_deleted_files):
        try:
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete=to_be_deleted_files
                )
        except ClientError as e:
            logging.error(e)
        except Exception as e:
            logging.error(f"There was an error deleting files, {e}")
        return


s3_service = S3Service(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
