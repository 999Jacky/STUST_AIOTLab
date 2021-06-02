import json

from flask import Flask, request
import Detection
import threading
import cv2
import io
import base64
import numpy as np

mutex = threading.Lock()
app = Flask(__name__)
IsBootComplete = False


def init():
    global IsBootComplete
    IsBootComplete = Detection.initDetection()


def readb64(uri):
    # encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(uri), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


@app.route("/detection", methods=["POST"])
def detection():
    global mutex, IsBootComplete
    if IsBootComplete is False:
        j = json.dumps({"status": False})
        return j
    mutex.acquire()
    imgBase64 = request.form["img"]
    # img = cv2.imdecode(numpy.fromstring(request.files['file'].read(), numpy.uint8), cv2.IMREAD_UNCHANGED)
    print(len(imgBase64))
    img = readb64(imgBase64)
    j = Detection.DetectionImg(img)
    mutex.release()
    return j


@app.route("/check")
def check():
    return "ok"


if __name__ == '__main__':
    init()
    app.run(host="0.0.0.0")
