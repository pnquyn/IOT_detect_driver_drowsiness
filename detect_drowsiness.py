import cv2
import dlib
import imutils
from imutils.video import VideoStream
from imutils import face_utils
import time
from scipy.spatial import distance as dist

left_eye_index = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
right_eye_index = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
mouth_index = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]
ear_thresh = 0.25
mar_thresh = 0.79
eye_closed_frame_num = 3
eye_closed_time_bound_sec = 2
eye_closed_hold_sec = 0.4
mouth_open_hold_sec = 2

class DrowsinessDetect:
    def __init__(self):
        print("-> Loading the predictor and detector...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        print("-> Starting Video Stream...")
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)
        self.start = time.perf_counter()

        self.ear_frame_num = 0
        self.curr_frame_num = 0

        self.ear, self.mar = 0, 0
        self.eye_is_closed, self.mouth_open = False, False
        self.eye_sleeping, self.is_yawning = False, False
        
        self.eye_close_start, self.yawning_start = -1, -1
        self.eye_closed_count, self.yawning_count = 0, 0

        self.drowsiness_eye, self.drowsiness_mouth = 0, 0
        self.eye_alert, self.mouth_alert = 0, 0

    def EAR(self, eye):
    # distance between the upper eye and lower eye
        eye_dist = dist.euclidean(eye[1], eye[5]) + dist.euclidean(eye[2], eye[4])
        # width of the eye
        eye_width = dist.euclidean(eye[0], eye[3])
        return eye_dist / (2 * eye_width)

    def avg_EAR(self, left_eye, right_eye):
        left_EAR = self.EAR(left_eye)
        right_EAR = self.EAR(right_eye)
        self.ear = (left_EAR + right_EAR) / 2
        return self.ear

    def MAR(self, mouth):
        # distance between the upper lip and lower lip
        mouth_dist = dist.euclidean(mouth[2], mouth[10]) + dist.euclidean(mouth[4], mouth[8])
        # width of the mouth
        mouth_width = dist.euclidean(mouth[0], mouth[6])
        self.mar = mouth_dist / (2 * mouth_width)
        return self.mar

    def print_mear_to_frame(self, frame, shape):
        cv2.putText(frame, "EAR: {:.2f}".format(self.ear), (450, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "MAR: {:.2f}".format(self.mar), (650, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if self.eye_sleeping:
            cv2.putText(frame, "Open your eyes!", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if self.is_yawning:
            cv2.putText(frame, "Yawning!", (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        for (i, (x, y)) in enumerate(shape):
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(frame, str(i), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
    def print_alert_to_frame(self, frame):
        if self.drowsiness_eye == 2:
            cv2.putText(frame, "Driver sleeping!!", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif self.drowsiness_eye == 1:
            cv2.putText(frame, "Wake up!!", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if self.drowsiness_mouth == 1:
            cv2.putText(frame, "Get some fresh air!!", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def deconstruct(self):
        cv2.destroyAllWindows()
        self.vs.stop()
    
    def detect_eyes_closed(self):
        if self.mouth_open == False and self.ear <= ear_thresh:
            self.ear_frame_num += 1
            if self.ear_frame_num >= eye_closed_frame_num and self.eye_is_closed == False:
                self.eye_is_closed = True
                self.eye_close_start = time.perf_counter()
        else:
            self.ear_frame_num = 0
            self.eye_is_closed = False
            self.eye_sleeping = False
        curr = time.perf_counter()
        if self.eye_is_closed and curr - self.eye_close_start >= eye_closed_hold_sec and self.eye_sleeping == False:
            self.eye_sleeping = True
            self.eye_closed_count += 1
            self.eye_alert = 0
        if self.eye_is_closed == True and curr - self.eye_close_start >= eye_closed_time_bound_sec:
            self.drowsiness_eye = 2
        elif self.eye_alert == 0 and self.eye_closed_count != 0 and self.eye_closed_count % 3 == 0:
            self.drowsiness_eye = 1
            self.eye_alert = 1
        else: 
            self.drowsiness_eye = 0
        return self.eye_is_closed
    
    def detect_yawning(self):
        if self.mar >= mar_thresh and self.mouth_open == False:
            self.yawning_start = time.perf_counter()
            self.mouth_open = True
        elif self.mar < mar_thresh:
            self.mouth_open = False
            self.is_yawning = False
        curr = time.perf_counter()
        if self.mouth_open and curr - self.yawning_start >= mouth_open_hold_sec and self.is_yawning == False:
            self.is_yawning = True
            self.yawning_count += 1
            self.mouth_alert = 0
        if self.mouth_alert == 0 and self.yawning_count != 0 and self.yawning_count % 2 == 0:
            self.drowsiness_mouth = 1
            self.mouth_alert = 1
        else: 
            self.drowsiness_mouth = 0
        return self.mouth_open
        
    def detect_drownsiness(self):
        frame = self.vs.read()
        frame = imutils.resize(frame, width=1024, height=576)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)
        # self.curr_frame_num += 1
        if len(rects) > 0:
            rect = rects[0]
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            left_eye = shape[left_eye_index[0]:left_eye_index[1]]
            right_eye = shape[right_eye_index[0]:right_eye_index[1]]
            mouth = shape[mouth_index[0]:mouth_index[1]]

            _,_ = self.avg_EAR(left_eye, right_eye), self.MAR(mouth)
            _ = self.detect_yawning()
            _ = self.detect_eyes_closed()
            self.print_mear_to_frame(frame, shape)
            
        # gui tin hieu
        self.print_alert_to_frame(frame)
        return frame

    
detect = DrowsinessDetect()
while True:
    frame = detect.detect_drownsiness()
    cv2.imshow("Detect", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

print(detect.eye_closed_count)
print(detect.yawning_count)
detect.deconstruct()