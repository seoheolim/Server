import logging

import cv2
from .detect_simple import detect
import face_recognition

# Open the input movie file


def make_data(video_path, img_path, video_name):
    video = cv2.VideoCapture(video_path)
    total_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    lmm_image = face_recognition.load_image_file(img_path)
    lmm_image = cv2.cvtColor(lmm_image, cv2.COLOR_BGR2RGB)
    fc_loc = detect(lmm_image)

    (left, bottom, right, top) = map(int, fc_loc[0].numpy())
    img_trim = lmm_image[bottom - int(bottom*0.1):top + int(top*0.1), left - int(left*0.1):right + int(right*0.1)]
    lmm_face_encoding = face_recognition.face_encodings(img_trim, model='large')[0]

    known_face_encodings = [lmm_face_encoding]

    frame_number = 0
    cnt = 0
    while True:
        ret, frame = video.read()
        frame_number += 1

        if not ret:
            break
        rgb_small_frame = frame[:, :, ::-1]
        logging.info(f"[Preprocessing] {frame_number}/{total_frame}")
        det = detect(rgb_small_frame)
        # yolo로 얼굴 detect하고 해당 좌표로 frame을 자르고 해당 이미지 저장
        if len(det) > 0:
            for tensor in det:
                (left, bottom, right, top) = tensor.numpy()
                left, right, top, bottom = map(int, [left, right, top, bottom])

                img_trim = frame[bottom - int(bottom*0.1):top + int(top*0.1), left - int(left*0.1):right + int(right*0.1)]
                face_encoding = face_recognition.face_encodings(img_trim, model='large')

                if len(face_encoding) > 0:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding[0])
                    if face_distances[0] < 0.4:
                        print("cnt: {}".format(cnt))
                        cv2.imwrite("dataset/data" + video_name + str(cnt) + ".png", frame[bottom:top, left:right])
                        cnt += 1

        if cnt > 200:
            break

    return cnt
