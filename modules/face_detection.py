import cv2
import os
from datetime import datetime

PHOTO_FOLDER = "photos"
if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)

if FACE_CASCADE.empty():
    print(f"ERROR: Cascade not found at {CASCADE_PATH}")
    print("Run: pip install opencv-contrib-python==4.10.0.84")
    exit()

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print("Webcam Started")
print("Press 'c' to Capture Photo | Press 'q' to Quit")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    status_text = "Face Not Detected"
    color = (0, 0, 255) 

    if len(faces) > 0:
        status_text = "Face Detected"
        color = (0, 255, 0) 

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, "Press 'c' to Capture | 'q' to Quit", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

   
    cv2.imshow("Face Detection - Online Exam", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(PHOTO_FOLDER, f"capture_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Image Saved Successfully: {filename}")

    elif key == ord('q'):
        print("Exiting...")
        break

cam.release()
cv2.destroyAllWindows()