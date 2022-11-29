import torch
import numpy as np

from models.experimental import attempt_load
from models.utilss.datasets import letterbox
from models.utilss.general import check_img_size, non_max_suppression, scale_boxes
from models.utilss.torch_utils import select_device, smart_inference_mode


WEIGHTS = 'models/weights/best.pt'
IMG_SIZE = 640
DEVICE = ''
AUGMENT = False
CONF_THRES = 0.25
IOU_THRES = 0.45
CLASSES = None
AGNOSTIC_NMS = False


def detect(SOURCE):
    source, weights, imgsz = SOURCE, WEIGHTS, IMG_SIZE

    # Initialize
    device = select_device(DEVICE)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, device=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if half:
        model.half()  # to FP16

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

    # Load image
    #img0 = cv2.imread(source)  # BGR
    assert source is not None, 'Image Not Found ' + source

    # Padded resize
    img = letterbox(source, imgsz, stride=stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t0 = smart_inference_mode()
    pred = model(img, augment=AUGMENT)[0]
    # Apply NMS
    pred = non_max_suppression(pred, CONF_THRES, IOU_THRES, classes=CLASSES, agnostic=AGNOSTIC_NMS)

    # Process detections
    det = pred[0]
            
    if len(det):
        # Rescale boxes from img_size to img0 size
        det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], source.shape).round()

    return det[:, :4]
