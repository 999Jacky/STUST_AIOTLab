import sys

sys.path.append("/home/nvidia/models/research")
import serial
from websocket import create_connection
import tensorflow as tf
import numpy as np
import cv2
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
import time
import json
import os
import datetime

print("Booting")
startTime = datetime.datetime.now()
c = 1
while datetime.datetime.now() - startTime < datetime.timedelta(seconds=10):
    c += 1
print("Initing")

# WS

ws = create_connection("ws://127.0.0.1:3000/ws")
print("Opening WS")
s = {
    "status": 0
}
j = json.dumps(s)
ws.send(j)

# USB serial

# serial_bluebud = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)
# serial_bluebud.write(("AI_Med System Stert\r\n").encode())
# serial_QR = serial.Serial('/dev/ttyUSB1', 9600, timeout=.1)
serial_QR = serial.Serial('/dev/barcode0', 9600, timeout=.1)

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("../..")

# What model to download.
# MODEL_NAME = '/home/nvidia/train_dummies_med/ssdMod1121/new_mod'
MODEL_NAME = '/home/nvidia/train_dummies_med/new_mod1201'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(
    '/home/nvidia/train_dummies_med/new_mod1201', 'object-detection.pbtxt')
# PATH_TO_LABELS = os.path.join('/home/nvidia/train_dummies_med/new_mod_ssdMobileNet', 'object-detection.pbtxt')

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(
    PATH_TO_LABELS, use_display_name=True)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


IMAGE_SIZE = (12, 8)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

os.system('v4l2-ctl -c focus_auto=0')
# time.sleep(0.5)
# os.system('v4l2-ctl -c focus_absolute=80')
time.sleep(0.5)
os.system('v4l2-ctl -c focus_absolute=110')

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
blue_blance = 0.75
# blue_blance=1

with detection_graph.as_default():
    with tf.Session(config=config) as sess:
        # Get handles to input and output tensors
        ret, frame = cap.read()

        image_np = frame
        print("second", image_np)
        ops = tf.get_default_graph().get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}
        tensor_dict = {}
        for key in [
            'num_detections', 'detection_boxes', 'detection_scores',
            'detection_classes'
        ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                    tensor_name)
        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

        # Run inference
        output_dict = sess.run(tensor_dict, feed_dict={
            image_tensor: np.expand_dims(image_np, 0)})

        boot = {
            "status": 5
        }
        bootDone = json.dumps(boot)
        ws.send(bootDone)
        print("\n\n\n\n\n\n\n\n\n\n###Stystem ON###\n\n")
        # os.system('v4l2-ctl -c focus_auto=0')
        # os.system('v4l2-ctl -c focus_absolute=80')
        # os.system('v4l2-ctl -c focus_absolute=90')

        while True:
            ret, frame = cap.read()
            b, g, r = cv2.split(frame)
            frame = cv2.merge(((b * blue_blance).astype(np.uint8), g, r))
            # cv2.imshow('frame', frame)
            QR_data = serial_QR.readline()
            QR_data = QR_data.decode()
            QR_data = QR_data.replace('\r', '').replace('\n', '')
            if len(QR_data) >= 1:
                print("QR:", QR_data)
                localtime = time.time()
                t = datetime.datetime.now()
                while datetime.datetime.now() - t < datetime.timedelta(milliseconds=350):
                    ret, frame = cap.read()
                    b, g, r = cv2.split(frame)
                    frame = cv2.merge(((b * blue_blance).astype(np.uint8), g, r))
                    # cv2.imshow('frame', frame)
                # image_np = frame.copy
                image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {
                    output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    'num_detections', 'detection_boxes', 'detection_scores',
                    'detection_classes'
                ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                            tensor_name)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

                # Run inference
                output_dict = sess.run(tensor_dict,
                                       feed_dict={image_tensor: np.expand_dims(image_np, 0)})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(
                    output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                    'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                class_name = "NONE"
                picMed = {}
                picMaxPercent = {}
                for i in range(0, output_dict['num_detections']):
                    score = output_dict['detection_scores'][i]
                    if score >= .5:
                        class_name = category_index[output_dict['detection_classes'][i]]['name']
                        if picMed.__contains__(class_name):
                            picMed[class_name] += 1
                            if picMaxPercent[class_name] < score:
                                picMaxPercent[class_name] = score
                        else:
                            picMed[class_name] = 1
                            picMaxPercent[class_name] = score

                time_1 = time.time() - localtime
                print("Time:", time_1)
                print("Med Class:", class_name)
                time_1 = round(time_1, 3)
                show_time = "spendtime:" + str(time_1) + " sec"

                # IMAGE_MDE_NAME,QR_CODE_MED_NAME,VERYFY{0:NOK|1:OK},MED_CONUT
                # serial_bluebud.write(("$" + str(QR_data) + "," + str(class_name) + "," + str(count) + "#\n").encode())
                # imgT = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')[:-5]
                imgT = "output"
                cv2.imwrite("/home/nvidia/img/{}_org.jpg".format(imgT), frame)
                meds = []
                meds2 = []
                for i, v in picMed.items():
                    med = {
                        "med_id": i,
                        "count": v
                    }
                    meds.append(med)
                enableFilter = None
                filterCount = 0
                for i, v in picMaxPercent.items():
                    if v >= .99:
                        enableFilter = i
                        filterCount += 1
                if enableFilter is not None and filterCount == 1:
                    med = {
                        "med_id": enableFilter,
                        "count": picMed[enableFilter]
                    }
                    meds2 = meds.copy()
                    meds.clear()
                    meds.append(med)
                send = {
                    "status": 3,
                    "qr": str(QR_data),
                    "cam": meds,
                    "img_url": imgT + "_org",
                    "un_filter": meds2
                }
                j = json.dumps(send)
                ws.send(j)

                # Visualization of the results of a detection.
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    output_dict['detection_boxes'],
                    output_dict['detection_classes'],
                    output_dict['detection_scores'],
                    category_index,
                    instance_masks=output_dict.get('detection_masks'),
                    use_normalized_coordinates=True,
                    line_thickness=4,
                    min_score_thresh=.5)
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                cv2.imwrite("/home/nvidia/img/{}.jpg".format(imgT), image_np)
                cv2.putText(image_np, show_time, (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 4, cv2.LINE_AA)
                # cv2.imshow('test', image_np)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('b'):
                blue_blance = blue_blance - 0.1
            elif k == ord('c'):
                blue_blance = blue_blance + 0.1

cap.release()
cv2.destroyAllWindows()
