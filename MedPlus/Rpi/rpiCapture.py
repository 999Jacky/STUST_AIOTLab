from gpiozero import Button
from time import sleep
import websocket
import threading
import time
import json
import cv2
import base64

button = Button(2)
isLastButtonPressed = False

ws = websocket.WebSocketApp("127.0.0.1")

DebugFlag = False


def SendJson(jsonStr):
    try:
        j = json.dumps(jsonStr)
        # print("send: " + j)
        ws.send(j)
    except Exception as e:
        print(e)
        ws.close()


def on_close(ws):
    print('WS disconnected')
    time.sleep(1)
    connect_websocket()  # retry


def on_open(ws):
    print('WS connected')


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def connect_websocket():
    global ws
    ws = websocket.WebSocketApp("ws://127.0.0.1:3000/ws", on_open=on_open, on_close=on_close, on_message=on_message,
                                on_error=on_error)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    print("Connecting WS")


def envSet(cam):
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
    # os.system('v4l2-ctl -c focus_auto=0')
    # os.system('v4l2-ctl -c focus_absolute=50')
    # os.system('v4l2-ctl -c focus_absolute=100')
    # os.system('v4l2-ctl -c sharpness=40')


def main():
    global isLastButtonPressed
    connect_websocket()
    cam = cv2.VideoCapture(0)
    envSet(cam)
    print("Start")
    while True:
        cam.read()
        if button.is_pressed:
            if not isLastButtonPressed:
                # capture
                isLastButtonPressed = True
                time.sleep(0.3)
                _, frame = cam.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imgBase64 = cv2.imencode('.jpg', frame)[1].tostring()
                imgBase64 = base64.b64encode(imgBase64)
                sendImgStr = {"function": "Img", "Img": str(imgBase64)[2:-1]}
                SendJson(sendImgStr)
                time.sleep(1)
        else:
            isLastButtonPressed = False
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
