import cv2
import requests

cap = cv2.VideoCapture(0)  # Mở webcam thật
while True:
    ret, frame = cap.read()
    if ret:
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(
            "http://127.0.0.1:1880/upload",
            files={"image": ("frame.jpg", img_encoded.tobytes())}
        )
        print(response.text)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()