import numpy as np
import tensorflow as tf
import cv2
import time
import json
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import base64

# ModelPath = "D:\\Temp\\TF\\ttt31" + '/saved_model'
# LabelMapPath = "D:\\Temp\\TF\\ttt31\\ttt.pbtxt"
#
ModelPath = "D:\\Temp\\TF\\model1_test" + '/saved_model'
LabelMapPath = "D:\\Temp\\TF\\model1_test\\data.pbtxt"
MinScore = 0.8

DebugWindow = 2  # 0->沒有 1->相機畫面 2->1+辨識結果
SaveImgPath = None

Timer = time.time()


def envSet():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)


def paintLabel(frame, detections, category_index, minScore):
    copyFrame = frame.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
        copyFrame,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=50,
        min_score_thresh=minScore,
        agnostic_mode=False)
    # copyFrame = cv2.cvtColor(copyFrame, cv2.COLOR_RGB2BGR)
    global Timer
    showTime = round(time.time() - Timer, 2)
    print("spend:" + str(showTime) + "s")
    if DebugWindow > 1:
        cv2.imshow("result", copyFrame)
    if SaveImgPath is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(SaveImgPath + "/{}_org.jpg".format("name"), frame)
        cv2.imwrite(SaveImgPath + "/{}.jpg".format("name"),
                    copyFrame)
    # copyFrame = cv2.cvtColor(copyFrame, cv2.COLOR_BGR2RGB)
    return copyFrame


def countMed(detections, category_index, QR_data, minScore):
    MedCount = {}
    for i in range(0, detections['num_detections']):
        score = detections['detection_scores'][i]
        scoreRange = minScore
        if category_index[detections['detection_classes'][i]]['name'] == QR_data:
            scoreRange = .5
        if score >= scoreRange:
            class_name = category_index[detections['detection_classes'][i]]['name']
            if MedCount.__contains__(class_name):
                MedCount[class_name] += 1
            else:
                MedCount[class_name] = 1
    return MedCount


detect_fn = lambda x: x + 1
category_index = {}


def LoadTensor():
    global Timer, detect_fn, category_index
    envSet()
    print("loading")
    detect_fn = tf.saved_model.load(ModelPath)
    category_index = label_map_util.create_category_index_from_labelmap(
        LabelMapPath, use_display_name=True)
    print("heating")

    blank_image = np.zeros((5, 5, 3), np.uint8)
    frame = blank_image
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis, ...]
    detect_fn(input_tensor)

    print("boot finish in time:" + str(time.time() - Timer) + "s")


def DetectionImg(img):
    global Timer, detect_fn, category_index
    frame = img
    if DebugWindow > 0:
        cv2.imshow("camera", frame)

    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    Timer = time.time()
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(
        np.int64)
    MedCount = countMed(detections, category_index, "", MinScore)
    print(MedCount)
    d = {"func": "detection", "Meds": MedCount}
    pImg = paintLabel(frame, detections, category_index, MinScore)
    imgBase64 = cv2.imencode('.jpg', pImg)[1].tostring()
    imgBase64 = base64.b64encode(imgBase64)
    sendStr = {"img": str(imgBase64)[2:-1], "Meds": MedCount, "status": True}
    j = json.dumps(sendStr)
    return j


def initDetection():
    envSet()
    LoadTensor()
    return True
