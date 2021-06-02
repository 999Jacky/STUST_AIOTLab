import sys

sys.path.append("/home/nvidia/models/research")
import serial
from websocket import create_connection
import tensorflow as tf
import numpy as np
import cv2
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
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
s = { "status": 0 }
j = json.dumps(s)
ws.send(j)

# USB serial
serial_QR = serial.Serial('/dev/barcode0', 9600, timeout=.1)

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("../..")

# What model to download.
# MODEL_NAME = '/home/nvidia/train_dummies_med/ssdMod1121/new_mod' #20191112
# MODEL_NAME = '/home/nvidia/train_dummies_med/new_mod_10med'
# MODEL_NAME = '/home/nvidia/train_dummies_med/new_mod_ssd'
# MODEL_NAME = '/home/nvidia/train_dummies_med/new_mod_0408'
# MODEL_NAME = '/home/nvidia/train_dummies_med/new_7'        #0510
# MODEL_NAME = '/home/nvidia/train_dummies_med/new_200M100'        #0511
# MODEL_NAME = '/home/nvidia/train_dummies_med/output_1124'
'''2020/05-21/Use'''
#MODEL_NAME = '/home/nvidia/train_dummies_med/new0603'        #0521
'''2020/06-16/Use'''
MODEL_NAME = '/home/nvidia/train_dummies_med/new0616'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.

'''2020/05-21/Use'''
# PATH_TO_LABELS = os.path.join('/home/nvidia/train_dummies_med/data38', 'object-detection.pbtxt')
# PATH_TO_LABELS = os.path.join('/home/nvidia/train_dummies_med/new_mod_ssdMobileNet', 'object-detection.pbtxt')
'''2020/06-16/Use'''
PATH_TO_LABELS = os.path.join('/home/nvidia/train_dummies_med/new0616', 'object-detection.pbtxt')

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(
    PATH_TO_LABELS, use_display_name=True)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

os.system('v4l2-ctl -c focus_auto=0')
os.system('v4l2-ctl -c focus_absolute=50')
os.system('v4l2-ctl -c focus_absolute=100')
os.system('v4l2-ctl -c sharpness=40')
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
blue_blance = 1
green_blance = 1
red_blance=1

savecount=0

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
            'num_detections',
            'detection_boxes',
            'detection_scores',
            'detection_classes'
        ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

        # Run inference
        output_dict = sess.run(tensor_dict, feed_dict={
            image_tensor: np.expand_dims(image_np, 0)})

        boot = { "status": 5 }
        bootDone = json.dumps(boot)
        ws.send(bootDone)
        print("\n\n\n\n\n\n\n\n\n\n\u001b[2J\u001b[0;0HStystem ON\n")

        while (True):
            ret, frame = cap.read()
            b, g, r = cv2.split(frame)
            frame = cv2.merge(((b * blue_blance).astype(np.uint8), (g * green_blance).astype(np.uint8), (r * red_blance).astype(np.uint8)))
            cv2.imshow('frame', frame)
            QR_data = serial_QR.readline()
            QR_data = QR_data.decode()
            QR_data = QR_data.replace('\r', '').replace('\n', '')
            if len(QR_data) >= 1:
                localtime = time.time()
                t = datetime.datetime.now()
                while datetime.datetime.now() - t < datetime.timedelta(milliseconds=350):
                    ret, frame = cap.read()
                    b, g, r = cv2.split(frame)
                    frame = cv2.merge(((b * blue_blance).astype(np.uint8), (g * green_blance).astype(np.uint8), (r * red_blance).astype(np.uint8)))
                    cv2.imshow('frame', frame)
                image_np = frame.copy
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
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
                class_name = "NONE"
                picMed = {}
                picMaxPercent = {}
                for i in range(0, output_dict['num_detections']):
                    score = output_dict['detection_scores'][i]
                    scorerang = .85
                    if category_index[output_dict['detection_classes'][i]]['name'] == QR_data:
                        scorerang = .5
                    if score >= scorerang:
                        class_name = category_index[output_dict['detection_classes'][i]]['name']
                        if picMed.__contains__(class_name):
                            picMed[class_name] += 1
                            # if picMaxPercent[class_name] < score:
                                # picMaxPercent[class_name] = score
                        else:
                            picMed[class_name] = 1
                            # picMaxPercent[class_name] = score
                meds = []
                medcount=0
                imgname = "output"
                for i, v in picMed.items():
                    med = {
                        "med_id": i,
                        "count": v
                    }
                    meds.append(med)
                    medcount += v
                send = {
                    "status": 3,
                    "qr": str(QR_data),
                    "cam": meds,
                    "img_url": imgname + "_org",
                    "un_filter": []
                }
                print(send)
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
                cv2.imwrite("/home/nvidia/img/{}_org.jpg".format(imgname), frame)
                cv2.imwrite("/home/nvidia/img/{}.jpg".format(imgname), image_np)
                time_1 = time.time() - localtime
                time_1 = round(time_1, 2)
                show_time = "Spend Time:" + str(time_1) + "S"
                show_count = "Med Count:" + str(medcount)
                cv2.putText(image_np, show_time, (8, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 4, cv2.LINE_AA)
                cv2.putText(image_np, show_count, (8, 465),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 4, cv2.LINE_AA)
                cv2.imshow('Test', image_np)
                print("Time:", time_1)
                print("QR:", QR_data)
                print("Med Class:", class_name)
                print("Med Count:", medcount)
                print("\n")
                # DeBug
                # cv2.imwrite("/home/nvidia/img/img_{}.jpg".format(savecount), frame)
                # cv2.imwrite("/home/nvidia/img/img_{}_out.jpg".format(savecount), image_np)
                savecount += 1
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('b'):
                blue_blance = blue_blance - 0.1
                print(blue_blance,",",green_blance,",",red_blance)
            elif k == ord('v'):
                blue_blance = blue_blance + 0.1
                print(blue_blance,",",green_blance,",",red_blance)
            elif k == ord('g'):
                green_blance = green_blance - 0.1
                print(blue_blance,",",green_blance,",",red_blance)
            elif k == ord('f'):
                green_blance = green_blance + 0.1
                print(blue_blance,",",green_blance,",",red_blance)
            elif k == ord('r'):
                red_blance = red_blance - 0.1
                print(blue_blance,",",green_blance,",",red_blance)
            elif k == ord('e'):
                red_blance = red_blance + 0.1
                print(blue_blance,",",green_blance,",",red_blance)

cap.release()
cv2.destroyAllWindows()
