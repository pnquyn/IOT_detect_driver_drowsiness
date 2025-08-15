import socket, base64
from detect import DrowsinessDetect
import numpy as np
import cv2
import json
import keyboard

user_id = "xaJWsOFeu0c1YVQsSJP8IUYNZSG2"

detect = DrowsinessDetect()
# Địa chỉ Node-RED server (node "tcp in" phải lắng nghe cổng này)
HOST, PORT = "127.0.0.1", 5050
# Tạo kết nối TCP client tới Node-RED
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((HOST, PORT))
print(f"Connected to Node-RED at {HOST}:{PORT}")

device_state = 0

while True:
    # Gọi hàm detect
    frame, drownsiness, ear, mar = detect.detect_drownsiness()

        # Encode frame thành Base64
    _, buffer = cv2.imencode('.jpg', frame)
    b64_img = base64.b64encode(buffer).decode('utf-8')

    packet = {
        "id": user_id,
        "image": b64_img,
        "drowsiness": drownsiness, 
        "ear": ear,
        "mar": mar,
        "device_state": device_state
    }
    if (device_state == 0):
        device_state = 1
    message = json.dumps(packet) + "\n"
    conn.sendall(message.encode('utf-8'))
    # print(f"frame {index} sent")
    if keyboard.is_pressed('q'):
        device_state = 2
        packet = {
        "id": user_id,
        "image": b64_img,
        "drowsiness": drownsiness, 
        "ear": ear,
        "mar": mar,
        "device_state": device_state
        }
        message = json.dumps(packet) + "\n"
        conn.sendall(message.encode('utf-8'))
        break

detect.deconstruct()
