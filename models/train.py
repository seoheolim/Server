import cv2
import numpy as np
import face_recognition
import os
import logging

# Path for face image database
path = 'dataset'


def get_images_and_labels(image_paths):
    face_samples = []
    ids = []
    
    for imagePath in image_paths:
        image = face_recognition.load_image_file(imagePath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_samples.append(image)
        ids.append(0)
        
    return face_samples, ids


def training(cnt, file_name, yml_path):
    logging.info("Training faces. It will take a few seconds. Wait ...")
    prefix = f"data{file_name}"

    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.startswith(prefix)]

    assert len(image_paths) == cnt

    faces, ids = get_images_and_labels(image_paths)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write(yml_path)
    # recognizer.save(file_name) #worked on Mac, but not on Pi

    # delete data files
    for image_path in image_paths:
        os.remove(image_path)

    # Print the numer of faces trained and end program
    logging.info(f"{len(np.unique(ids))} faces trained. Exiting Program")
