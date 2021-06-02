import numpy as np
import tensorflow as tf
import cv2
import os
import serial
import time
import sys
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

ModelPath = "D:\\Temp\\TF\\ttt31" + '/saved_model'
LabelMapPath = "D:\\Temp\\TF\\ttt31\\ttt.pbtxt"
QrCodeDev = None  # /dev/barcode0
MinScore = 0.8

DebugWindow = 2  # 0->沒有 1->相機畫面 2->1+辨識結果
RealTimeTest = True
SaveImgPath = None

Timer = time.time()


def envSet(cam):
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
    os.system('v4l2-ctl -c focus_auto=0')
    os.system('v4l2-ctl -c focus_absolute=50')
    os.system('v4l2-ctl -c focus_absolute=100')
    os.system('v4l2-ctl -c sharpness=40')
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
    copyFrame = cv2.cvtColor(copyFrame, cv2.COLOR_RGB2BGR)
    global Timer
    showTime = round(time.time() - Timer, 2)
    if RealTimeTest is True:
        fpsTxt = round(1 / showTime, 1)
        cv2.putText(copyFrame, "fps:" + str(fpsTxt), (8, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 4, cv2.LINE_AA)
    else:
        cv2.putText(copyFrame, str(showTime) + "s", (8, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 4, cv2.LINE_AA)
    if DebugWindow > 1:
        cv2.imshow("result", copyFrame)
        if RealTimeTest is True:
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                cv2.destroyAllWindows()
                sys.exit(0)
    if SaveImgPath is not None and RealTimeTest is False:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(SaveImgPath + "/{}_org.jpg".format("name"), frame)
        cv2.imwrite(SaveImgPath + "/{}.jpg".format("name"),
                    copyFrame)


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


def main():
    global Timer
    cam = cv2.VideoCapture(0)
    envSet(cam)
    if QrCodeDev is not None:
        serial_QR = serial.Serial(QrCodeDev, 9600, timeout=.1)
    QR_data = ""
    print("loading")
    detect_fn = tf.saved_model.load(ModelPath)
    category_index = label_map_util.create_category_index_from_labelmap(
        LabelMapPath, use_display_name=True)
    print("heating")
    _, frame = cam.read()
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis, ...]
    detect_fn(input_tensor)
    print("boot time:" + str(time.time() - Timer) + "s")
    while True:
        _, frame = cam.read()
        if DebugWindow > 0 and RealTimeTest is False:
            cv2.imshow("camera", frame)
        if QrCodeDev is not None:
            QR_data = serial_QR.readline()
            QR_data = QR_data.decode()
            QR_data = QR_data.replace('\r', '').replace('\n', '')
            if len(QR_data) == 0:
                continue
        if RealTimeTest is False:
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('d'):
                pass
            else:
                continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
        MedCount = countMed(detections, category_index, QR_data, MinScore)
        print(MedCount)
        paintLabel(frame, detections, category_index, MinScore)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
