import numpy as np
import tensorflow as tf
import cv2
import time
import sys
import websocket
import threading
import json
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import os
import base64

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
ModelPath = "F:\\FTemp\\TF2\\20201211_4MED_60P\\" + '/saved_model'
# ModelPath = "D:\\Temp\\TF\\20201211_4MED_60P" + '/saved_model'
LabelMapPath = "F:\\FTemp\\TF2\\20201211_4MED_60P\\20201211_4MED_60P.pbtxt"
# LabelMapPath = "D:\\Temp\\TF\\20201211_4MED_60P\\20201211_4MED_60P.pbtxt"
MinScore = 0.8

DebugWindow = 0  # 0->沒有 1->相機畫面 2->1+辨識結果
RealTimeTest = True
SaveImgPath = None

Timer = time.time()
ws = websocket.WebSocketApp("127.0.0.1")
wst = threading.Thread()
StopDetection = True
isWsConnected = False
isSendBootDone = False


def SendJson(jsonStr):
    try:
        j = json.dumps(jsonStr)
        # print("send: " + j)
        ws.send(j)
    except Exception as e:
        print(e)
        ws.close()


def on_close(ws):
    global isSendBootDone, isWsConnected, StopDetection
    print('WS disconnected')
    time.sleep(1)
    isSendBootDone = False
    isWsConnected = False
    StopDetection = True
    connect_websocket()  # retry


def on_open(ws):
    global isWsConnected
    print('WS connected')
    isWsConnected = True


def on_message(ws, message):
    print(message)
    global StopDetection
    data = json.loads(message)
    func = data["function"]
    if func == "StartDetection":
        StopDetection = False
    if func == "StopDetection":
        StopDetection = True


def on_error(ws, error):
    print(error)


def connect_websocket():
    global ws, wst
    ws = websocket.WebSocketApp("ws://127.0.0.1:3001/ws", on_open=on_open, on_close=on_close, on_message=on_message,
                                on_error=on_error)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    print("Connecting WS")


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

    imgBase64 = cv2.imencode('.jpg', copyFrame)[1].tostring()
    imgBase64 = base64.b64encode(imgBase64)
    sendImgStr = {"function": "Img", "Img": str(imgBase64)[2:-1]}
    SendJson(sendImgStr)


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
    global Timer, isSendBootDone, isWsConnected, StopDetection
    connect_websocket()
    cam = cv2.imread("F:\\FTemp\\TF2\\Med_4_20201211173552.jpg")
    # cam = cv2.imread("D:\\Temp\\TF\\20201211_4MED_60P\\Med_4_20201211173554.jpg")
    envSet()
    print("loading")
    detect_fn = tf.saved_model.load(ModelPath)
    category_index = label_map_util.create_category_index_from_labelmap(
        LabelMapPath, use_display_name=True)
    print("heating")
    input_tensor = tf.convert_to_tensor(cam)
    input_tensor = input_tensor[tf.newaxis, ...]
    detect_fn(input_tensor)
    print("boot time:" + str(time.time() - Timer) + "s")
    while True:
        isWaiting = False
        while StopDetection:
            if not isSendBootDone:
                if isWsConnected:
                    s = {"function": "BootFinish"}
                    SendJson(s)
                    isSendBootDone = True
            if not isWaiting:
                isWaiting = True
                print("waiting barcode input")

        print("detectionING")
        frame = cam
        if DebugWindow > 0 and RealTimeTest is False:
            cv2.imshow("camera", frame)
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
        MedCount = countMed(detections, category_index, "", MinScore)
        print(MedCount)
        d = {"function": "detection", "Meds": MedCount}
        SendJson(d)
        paintLabel(frame, detections, category_index, MinScore)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
