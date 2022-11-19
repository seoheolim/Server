import logging
import json
import datetime

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config.config import MAIL_FROM, MAIL_SERVER, MAIL_USERNAME, MAIL_STARTTLS,\
    MAIL_PORT, MAIL_FROM_NAME, MAIL_PASSWORD, MAIL_SSL_TLS, USE_CREDENTIALS, VALIDATE_CERTS, S3_URL, LOGO_URL
from app.db.redis import redis_db


conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS,
    VALIDATE_CERTS=VALIDATE_CERTS
)


async def send_email(email: str, video_path: str):
    logging.info(f"start sending email to {email}")
    file_restored_path = f"result/{video_path}"
    video_download_path = S3_URL + "/" + file_restored_path

    html = EMAIL_TEMPLATE\
        .format(title="[HIDE] 영상 변환이 완료되었습니다", logo_url=LOGO_URL,
                line1="영상은 24시간 보관 후 삭제될 예정이니,", line2="시간 내 다운로드 해주시길 바랍니다.",
                line3="아래 download 버튼을 클릭하시면 변환된 영상을 확인할 수 있습니다.",
                download_path=video_download_path)

    message = MessageSchema(
        subject="[HIDE] 영상 변환이 완료되었습니다",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)

    log = {
        "video_path": file_restored_path,
        "exp": False,
        "email": email,
        "saved_time": datetime.datetime.now().strftime("%Y%m%d")
    }
    logging.info(video_path.split(".")[0])
    redis_db.set("LOG"+video_path.split(".")[0], json.dumps(log))
    logging.info(f"sent email to {email}")


EMAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head> <title> title </title> </head>
<body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
<div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
  <div style="margin: 0 auto; width: 90%; text-align: center;">
    <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">{title}</h1>
    <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
        <img width="200" height="200" src = {logo_url} alt="Hide-Logo">
        <h3 style="font-size:24px">{line1}</h3>
        <h3 style="font-size: 24px;">{line2}</h3>
      <p style="margin-bottom: 30px;">{line3}</p>
      <a style="display: block; margin: 0 auto; border: none; background-color: rgba(255, 214, 10, 1);
       color: white; width: 200px; line-height: 24px; padding: 10px; font-size: 24px; border-radius: 10px;
       cursor: pointer; text-decoration: none;"
        href="{download_path}"
        target="_blank"
      >
        download
      </a>
    </div>
  </div>
</div>
</body>
</html>'''
