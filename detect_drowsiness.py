import cv2
import dlib
import imutils
from imutils.video import VideoStream
from imutils import face_utils
import time
from scipy.spatial import distance as dist

EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.79
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0

class DrowsinessDetect:
    def __init__(self):
        print("-> Loading the predictor and detector...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        print("-> Starting Video Stream...")
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)

        self.left_eye_index = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        self.right_eye_index = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        self.mouth_index = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]
        self.ear_thresh = 0.25
        self.mar_thresh = 0.79
        self.ear_frame_num = 3
        self.counter = 0 

        self.ear, self.mar = 0, 0
        self.eye_is_closed, self.is_yawning = False, False

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

    def print_to_frame(self, frame, shape):
        cv2.putText(frame, "EAR: {:.2f}".format(self.ear), (450, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "MAR: {:.2f}".format(self.mar), (650, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if self.eye_is_closed:
            cv2.putText(frame, "Eyes Closed!", (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if self.is_yawning:
            cv2.putText(frame, "Yawning!", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        for (i, (x, y)) in enumerate(shape):
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(frame, str(i), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

    def deconstruct(self):
        cv2.destroyAllWindows()
        self.vs.stop()
    
    def detect_eyes_closed(self):
        if self.ear < self.ear_thresh:
            self.counter += 1
            if self.counter >= self.ear_frame_num:
                self.eye_is_closed = True
        else:
            self.counter = 0
            self.eye_is_closed = False
        return self.eye_is_closed
    
    def detect_yawning(self):
        if self.mar > self.mar_thresh:
            self.is_yawning = True
        else:
            self.is_yawning = False
        return self.is_yawning
        
    def dectect_drownsiness(self):
        while True:
            frame = self.vs.read()
            frame = imutils.resize(frame, width=1024, height=576)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)

            for rect in rects:
                # (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
                # cv2.rectangle(frame, (bX, bY), (bX + bW, bY + bH), (0, 255, 0), 1)
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                left_eye = shape[self.left_eye_index[0]:self.left_eye_index[1]]
                right_eye = shape[self.right_eye_index[0]:self.right_eye_index[1]]
                mouth = shape[self.mouth_index[0]:self.mouth_index[1]]

                _,_ = self.avg_EAR(left_eye, right_eye), self.MAR(mouth)

                _,_ = self.detect_eyes_closed(), self.detect_yawning()
                self.print_to_frame(frame, shape)

            cv2.imshow("Detect Drowsiness", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

detect = DrowsinessDetect()
detect.dectect_drownsiness()
detect.deconstruct()


