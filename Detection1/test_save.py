import glob
import os
import sys
import time
sys.path.append("../..")
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from object_detection.utils import ops as utils_ops

# This is needed since the notebook is stored in the object_detection folder.


# This is needed to display the images.


# What model to download.
MODEL_NAME = '/mnt/d/AI/med/train_dummies_med/new_mod1202'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(
    '/mnt/d/AI/med/train_dummies_med/new_mod1202', 'object-detection.pbtxt')

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


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = '/mnt/d/AI/med/train_dummies_med/test_images2'
# PATH_TO_TEST_IMAGES_DIR = '/mnt/d/AI/med/cvTest/'

TEST_IMAGE_PATHS = glob.glob(PATH_TO_TEST_IMAGES_DIR + '/*.jpg')

# TEST_IMAGE_PATHS = [os.path.join(
#     PATH_TO_TEST_IMAGES_DIR, 'img{}.jpg'.format(i)) for i in range(1, 31)]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

# TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'med{}.jpg'.format(i)) for i in range(1,4) ]

# Size, in inches, of the output images.
# IMAGE_SIZE = (12, 8)


def shapenImg(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)
    dst = cv2.filter2D(image, -1, kernel=kernel)
    return dst


# def claheImg(Image):
#     # Fail
#     clahe = cv2.createCLAHE()
#     equal_img = clahe.apply(Image)
#     return equal_img


# def contrast_brightness_image(src1, a, g):
#     h, w, ch = src1.shape  # 获取shape的数值，height和width、通道

#     # 新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)
#     src2 = np.zeros([h, w, ch], src1.dtype)
#     dst = cv2.addWeighted(src1, a, src2, 1-a, g)  # addWeighted函数说明如下
#     return dst


# def hisEqulColor(img):
#     ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
#     channels = cv2.split(ycrcb)
#     # print(len(channels))
#     cv2.equalizeHist(channels[0], channels[0])
#     cv2.merge(channels, ycrcb)
#     cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
#     return img


with detection_graph.as_default():
    with tf.Session() as sess:
        for image_path in TEST_IMAGE_PATHS:
            allTime = time.clock()
            # Get handles to input and output tensors
            image = Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = load_image_into_numpy_array(image)

            imgPross = time.clock()
            # image_np = shapenImg(image_np)
            # image_np = claheImg(image_np)
            # image_np = contrast_brightness_image(image_np, 1.2, 15)
            # image_np = hisEqulColor(image_np)
            imgPross2 = time.clock()
            print("額外圖片處理時間{}".format(imgPross2 - imgPross))
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
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
                # The following processing is only for single image
                detection_boxes = tf.squeeze(
                    tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(
                    tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
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
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
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
            nowtime = time.clock()
            time_1 = nowtime - localtime
            print("辨識時間:", time_1)

            count = 0
            for i in range(0, output_dict['num_detections']):
                if output_dict['detection_scores'][i] >= .5:
                    count += 1
            print("box count:{}".format(count))
            # Visualization of the results of a detection.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                output_dict['detection_boxes'],
                output_dict['detection_classes'],
                output_dict['detection_scores'],
                category_index,
                instance_masks=output_dict.get('detection_masks'),
                use_normalized_coordinates=True,
                line_thickness=1,
                min_score_thresh=.5,
                max_boxes_to_draw=100)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            cv2.putText(image_np, "{}".format(count), (5, 450), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 1, cv2.LINE_AA)
            # cv2.imshow('test', image_np)
            # cv2.waitKey(1)
            cv2.imwrite(image_path, image_np)
            alltime2 = time.clock()
            print("總共時間：{}".format(alltime2 - allTime))
            print()
cv2.destroyAllWindows()
