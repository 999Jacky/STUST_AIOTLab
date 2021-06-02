import glob
import os
import sys
import datetime
from Detection1 import util

sys.path.append("../..")
sys.path.append("K:\\Python\\models\\research")
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# What model to download.
MODEL_NAME = 'K:\\Python\\train_dummies_med\\new_mod_ssd'
# MODEL_NAME = 'D:\\Python\\train_dummies_med_Xav\\train_dummies_med\\new_mod_ssd'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(
    'K:\\Python\\train_dummies_med\\data_ssd', 'object-detection.pbtxt')
# 'D:\\Python\\train_dummies_med_Xav\\train_dummies_med\\data_ssd', 'object-detection.pbtxt')

# outImgPATH = "D:\\Python\\train_dummies_med_Xav\\train_dummies_med\\outImg"
outImgPATH = "K:\\Python\\train_dummies_med\\outImg"

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(
    PATH_TO_LABELS, use_display_name=True)


def load_image_into_numpy_array(image2):
    (im_width, im_height) = image2.size
    return np.array(image2.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


PATH_TO_TEST_IMAGES_DIR = 'K:\\Python\\train_dummies_med\\test_images2'
# PATH_TO_TEST_IMAGES_DIR = 'D:\\Python\\train_dummies_med_Xav\\train_dummies_med\\test_images'

TEST_IMAGE_PATHS = glob.glob(PATH_TO_TEST_IMAGES_DIR + '/*.jpg')

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
with detection_graph.as_default():
    with tf.Session(config=config) as sess:
        for image_path in TEST_IMAGE_PATHS:
            image = Image.open(image_path)
            image_np = load_image_into_numpy_array(image)

            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
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

            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image_np, 0)})

            output_dict['num_detections'] = int(
                output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]

            count = 0
            for i in range(0, output_dict['num_detections']):
                if output_dict['detection_scores'][i] >= .8:
                    count += 1
            print("box count:{}".format(count))
            # Visualization of the results of a detection.
            image_np2 = image_np.copy()
            image_np3 = image_np.copy()
            imgT = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-5]
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                output_dict['detection_boxes'],
                output_dict['detection_classes'],
                output_dict['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                line_thickness=1,
                min_score_thresh=.8,
                max_boxes_to_draw=100)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            cv2.putText(image_np, "{}".format(count), (5, 450), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 1, cv2.LINE_AA)

            output_dict['detection_scores'] = util.del_repeat_box(output_dict['detection_boxes'],
                                                                  output_dict['detection_scores'], 0.8)
            cv2.imwrite("{}\\{}.jpg".format(outImgPATH, imgT), image_np)
            print()
cv2.destroyAllWindows()
exit(0)
