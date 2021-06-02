import websocket
import json

try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print("on Recv")
    print(message)
    data = {
        "status": 2
    }
    json_str = json.dumps(data)
    ws.send(json_str)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        data = {
            "status": 1
        }
        json_str = json.dumps(data)
        ws.send(json_str)
        time.sleep(1)
        print("thread terminating...")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:3000/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
