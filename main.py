import re
import io
import time
import json
import os
import numpy as np
from PIL import Image
from collections import deque
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, Response, request
from functools import wraps

# Model
from davis import detect_objects, start_session


app = Flask(__name__)

###########################################################################
# LOGGING                                                                 #
###########################################################################
# app logging
appLogHandler = RotatingFileHandler('./logs/info.log', maxBytes=1000,
                                    backupCount=1)
appLogHandler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(appLogHandler)

# python logging
logHandler = RotatingFileHandler('./logs/python_info.log',  mode='a',
                                 maxBytes=5*(1024**2), backupCount=1,)
logHandler.setLevel(logging.INFO)
py_log = logging.getLogger('root')
py_log.setLevel(logging.INFO)
py_log.addHandler(logHandler)


py_log.info('##### STARTING DAVIS SERVER #####')


###########################################################################
# MODEL CONFIGURATION                                                     #
###########################################################################
CWD_PATH = os.getcwd()
MODEL_CONFIG_PATH = os.path.join(CWD_PATH, 'model_cfg.json')
selected_model = json.load(open(MODEL_CONFIG_PATH))

MODEL_FOLDER = selected_model['model_folder']
MODEL_JSON = selected_model['model_config_file']

MODEL_CFG = os.path.join(CWD_PATH, MODEL_FOLDER, MODEL_JSON)

py_log.info('Using model %s', MODEL_JSON)

blank_img = np.zeros((360, 480, 3), dtype=np.uint8)
blank_img.fill(255)

output_q = deque(maxlen=60)
output_q.append(blank_img)


###########################################################################
# TENSORFLOW                                                              #
###########################################################################

py_log.info('Initializing model at ' + time.strftime('%Y-%m-%d-%H:%M:%S',
            time.gmtime()))

# Gets session and detection graph
sess, detection_graph, label_map, categories, category_index = \
                                                   start_session(MODEL_CFG)

# Pass blank image to session to initialize the model
detect_objects(output_q[0], sess, detection_graph, category_index)

py_log.info('Model loaded at ' + time.strftime('%Y-%m-%d-%H:%M:%S',
            time.gmtime()))
py_log.info('##### END OF SERVER BOOT PROCESS #####')


###########################################################################
# FLASK APP                                                               #
###########################################################################
is_stream = 0
youtube_stream = 0


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'teste'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def gen(output_q):
    """Video streaming generator function"""
    py_log.debug('gen was activated')
    while True:
        time.sleep(0.05)
        if is_stream == 0:
            py_log.debug('is_stream is false, outputting zeros')
            output = blank_img
        else:
            if len(output_q) > 1:
                # Get annotated frame from queue
                output = output_q.popleft()
                py_log.debug("Processing and removing image from queue")
                py_log.debug("New queue size: %d", len(output_q))
            else:
                py_log.debug("Processing image from queue but not removing")
                py_log.debug("New queue size: %d", len(output_q))
                output = output_q[0]

        # Convert output to bytes
        out_img = Image.fromarray(output, 'RGB')
        img_io = io.BytesIO()
        out_img.save(img_io, 'JPEG')

        py_log.debug('Yielding new image at '
                     + time.strftime('%Y-%m-%d-%H:%M:%S', time.gmtime()))

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_io.getvalue()
               + b'\r\n')


@app.route('/')
def index():
    """Davis homepage"""
    return render_template('index.html')


@app.route('/live_demo')
def live_demo():
    """Davis homepage"""
    return render_template('live_demo.html')


@app.route('/webcam_admin', methods=['GET', 'POST'])
@requires_auth
def webcam_admin():
    """Webcam streaming home page"""
    if request.method == 'GET':

        return render_template('webcam_admin.html')

    if request.method == 'POST':
        jquery_input = request.form
        global is_stream
        is_stream = int(jquery_input['is_stream'])
        image_b64 = jquery_input['frame_data']

        py_log.debug('is_stream: %s', is_stream)

        if is_stream:
            py_log.debug('activated is_stream==1')

            # Get image data from JS
            image_data = re.sub('^data:image/.+;base64,', '', image_b64)
            image_data = image_data.decode('base64')
            frame = np.array(Image.open(io.BytesIO(image_data)))

            # Get annotated frame from model
            output = detect_objects(frame, sess, detection_graph, category_index)

            # Adds output to queue
            output_q.append(output)
            py_log.debug("Adding image to queue - q_size: %d", len(output_q))

        return ''


@app.route('/camera_feed')
def camera_feed():
    """Webcam streaming route. Put this in the src attrib of an img tag"""
    return Response(gen(output_q),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':

    ###########################################################################
    # SSL CONTEXT                                                             #
    ###########################################################################
    cer = os.path.join(CWD_PATH, 'cert.pem')
    key = os.path.join(CWD_PATH, 'key.pem')
    context = (cer, key)

    app.run(debug=True, threaded=True, use_reloader=False,
            host='0.0.0.0', ssl_context=context)
