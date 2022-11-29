import logging
import os

import cv2
import numpy as np

from .detect_simple import detect
from .preprocess import make_data
from .train import training

CONFIDENCE = 85


def mosaic(video_path, image_path, entire_video_name, option):
    logging.info(f"[Mosaic] option: {option}")

    cnt = make_data(video_path, image_path, entire_video_name)
    yml_path = f'models/trainer{entire_video_name}.yml'

    training(cnt, entire_video_name, yml_path)

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.read(yml_path)

    # Open the input movie file
    video = cv2.VideoCapture(video_path)
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'FMP4')
    converted_video_path = f"temp/temp-{entire_video_name}.mp4"

    output_video = cv2.VideoWriter(converted_video_path, fourcc, fps, (
        int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    logging.info("processing start!")

    match_faces = []
    dis_match_faces = []
    locations = []
    frame_number = 0
    while True:
        ret, frame = video.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_small_frame = frame[:, :, ::-1]
        det = detect(rgb_small_frame)

        logging.info(f"[Processing] {frame_number}/{length}")
        if len(det) > 0:
            for tensor in det:
                (left, bottom, right, top) = tensor.numpy()
                left, right, top, bottom = map(int, [left, right, top, bottom])

                _, confidence = recognizer.predict(gray[bottom:top, left:right])
                # Check if confidence is less them 100 ==> "0" is perfect match

                locations.append([confidence, [top, right, bottom, left]])

        faces = []

        if locations:
            candidate_idx = locations.index(min(locations, key=lambda x: x[0]))

            if locations[candidate_idx][0] < CONFIDENCE:
                match_faces = [locations[candidate_idx][1]]
                locations.pop(candidate_idx)

        for conf, coord in locations:
            dis_match_faces.append(coord)

        if option == "Only":
            faces = match_faces
        else:
            faces = dis_match_faces

        for face in faces:
            (top, right, bottom, left) = face
            blur = frame[bottom:top, left:right]
            blur = cv2.blur(blur, (50, 50))
            frame[bottom:top, left:right] = blur

        locations = []

        match_faces = []
        dis_match_faces = []

        output_video.write(frame)
        frame_number += 1

    os.remove(yml_path)

    logging.info("processing done!")
    video.release()
    cv2.destroyAllWindows()

    return converted_video_path
