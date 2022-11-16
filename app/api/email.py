import logging
import json

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config import MAIL_FROM, MAIL_SERVER, MAIL_USERNAME, MAIL_STARTTLS,\
    MAIL_PORT, MAIL_FROM_NAME, MAIL_PASSWORD, MAIL_SSL_TLS, USE_CREDENTIALS, VALIDATE_CERTS


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


async def send_email(email: str, loc: str):
    logging.info(f"start sending email to {email}")

    loc = json.loads(loc)
    html = EMAIL_TEMPLATE.format("[HIDE] 영상 변환이 완료되었습니다","변환이 완료되었습니다!", "아래 확인하기 버튼을 클릭하시면 변환된 영상을 확인할 수 있습니다. ", loc["video_loc"], "확인하기")
    message = MessageSchema(
        subject="[HIDE] 영상 변환이 완료되었습니다",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    logging.info(f"sent email to {email}")


EMAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head> <title> title </title> </head>
<body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
<div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
  <div style="margin: 0 auto; width: 90%; text-align: center;">
    <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">{0}</h1>
    <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
      <h3 style="margin-bottom: 100px; font-size: 24px;">{1}</h3>
      <p style="margin-bottom: 30px;">{2}</p>
      <a style="display: block; margin: 0 auto; border: none; background-color: rgba(255, 214, 10, 1);
       color: white; width: 200px; line-height: 24px; padding: 10px; font-size: 24px; border-radius: 10px; 
       cursor: pointer; text-decoration: none;"
        href="https://hide-file.s3.ap-northeast-2.amazonaws.com/{3}"
        target="_blank"
      >
        {4}
      </a>
    </div>
  </div>
</div>
</body>
</html>'''
