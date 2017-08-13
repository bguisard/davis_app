import tensorflow as tf
import numpy as np
import os
import json

# from TF model zoo - version provided on repo may be outdated
from object_detection.utils import label_map_util as l_util
from object_detection.utils import visualization_utils as vis_util


def detect_objects(image_np, sess, detection_graph, category_index):
    # Expand dims as the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where an object was detected
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects
    # Score is shown on the result image, together with the class label
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    # Visualization of the results of a detection
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=5)

    return image_np


def start_session(MODEL_CFG):

    # Load model details from file
    model_details = json.load(open(MODEL_CFG))

    CWD_PATH = os.getcwd()
    MODEL_NAME = model_details['model_folder']
    MODEL_FILE = model_details['model_filename']
    LABELS_FILE = model_details['labels_filename']
    NUM_CLASSES = model_details['number_of_classes']
    PATH_TO_CKPT = os.path.join(CWD_PATH, 'models', MODEL_NAME, MODEL_FILE)
    PATH_TO_LABELS = os.path.join(CWD_PATH, 'models', 'labels', LABELS_FILE)

    # Load label map
    label_map = l_util.load_labelmap(PATH_TO_LABELS)
    categories = l_util.convert_label_map_to_categories(label_map,
                                                        max_num_classes=NUM_CLASSES,
                                                        use_display_name=True)
    category_index = l_util.create_category_index(categories)

    # Starts Session
    # TF Config
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    detection_graph = tf.Graph()

    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph, config=config)

    return sess, detection_graph, label_map, categories, category_index
