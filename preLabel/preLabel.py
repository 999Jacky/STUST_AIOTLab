import cv2
import numpy as np
import six.moves.urllib as urllib
import tensorflow as tf
from matplotlib import pyplot as plt
from PIL import Image
import PIL.ImageDraw as ImageDraw
import glob
import xml.etree.ElementTree as ET
import os
import time

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

MODEL_NAME = '/mnt/c/Users/pc1/Desktop/AI/Med/train_dummies_med/new_mod'
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

PATH_TO_LABELS = os.path.join(
    '/mnt/c/Users/pc1/Desktop/AI/Med/train_dummies_med/data', 'object-detection.pbtxt')

PATH_TO_TEST_IMAGES_DIR = '/mnt/c/Users/pc1/Desktop/AI/Med/train_dummies_med/test_images2'


def addElememt(name, value):
    t = ET.Element(name)
    t.text = '{}'.format(value)
    return t


def getLabelName(index, i):
    return index[i]['name']


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

TEST_IMAGE_PATHS = glob.glob(PATH_TO_TEST_IMAGES_DIR + '/*.jpg')

with detection_graph.as_default():
    with tf.Session() as sess:
        for image_path in TEST_IMAGE_PATHS:
            image = Image.open(image_path)
            image_np = load_image_into_numpy_array(image)

            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            localtime = time.clock()
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {
                output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)
            if 'detection_masks' in tensor_dict:
                detection_boxes = tf.squeeze(
                    tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(
                    tensor_dict['detection_masks'], [0])
                real_num_detection = tf.cast(
                    tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [
                    real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                    real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image_np.shape[0], image_np.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image_np, 0)})

            output_dict['num_detections'] = int(
                output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]

            nowtime = time.clock()
            time_1 = nowtime - localtime
            print("time:", time_1)

            draw = ImageDraw.Draw(image)
            im_width, im_height = image.size

            foladerName = image_path.split("/")[-2]
            imageName = image_path.split("/")[-1]
            imageCount = imageName.split(".")[0]
            xmlTree = ET.parse(os.path.join(os.path.abspath(
                os.path.dirname(__file__)), "xml.sample"))
            xmlTree.find("filename").text = imageName
            xmlTree.find("folder").text = foladerName
            root = xmlTree.getroot()

            for i in range(0, output_dict['num_detections']):
                if output_dict['detection_scores'][i] >= .9:  # 90%以上才框
                    ymin, xmin, ymax, xmax = output_dict['detection_boxes'][i]
                    # (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                    #   ymin * im_height, ymax * im_height)
                    # 轉座標
                    pos = np.array([xmin * im_width, xmax * im_width,
                                    ymin * im_height, ymax * im_height], dtype=np.float64)
                    posInt = pos.astype(np.int32)
                    (left, right, top, bottom) = posInt
                    # Xml處理
                    xmlObj = ET.Element("object")
                    labelName = getLabelName(
                        category_index, output_dict['detection_classes'][i])
                    objName = addElememt("name", labelName)
                    objPose = addElememt("Pose", "Unspecified")
                    objTr = addElememt("truncated", 0)
                    objDiff = addElememt("difficult", 0)
                    objBox = ET.Element("bndbox")
                    objBox.append(addElememt("xmin", left))
                    objBox.append(addElememt("ymin", top))
                    objBox.append(addElememt("xmax", right))
                    objBox.append(addElememt("ymax", bottom))

                    xmlObj.append(objName)
                    xmlObj.append(objPose)
                    xmlObj.append(objTr)
                    xmlObj.append(objDiff)
                    xmlObj.append(objBox)

                    root.append(xmlObj)

                    xmlTree.write(os.path.join(
                        PATH_TO_TEST_IMAGES_DIR, imageCount+".xml"))
print("Done")
