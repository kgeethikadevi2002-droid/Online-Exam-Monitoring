import cv2
import os
from datetime import datetime

# 1. SETUP FOLDERS AND CASCADE
PHOTO_FOLDER = "photos"
if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

# Use OpenCV's built-in cascade file
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)

if FACE_CASCADE.empty():
    print(f"ERROR: Cascade not found at {CASCADE_PATH}")
    print("Run: pip install opencv-contrib-python==4.10.0.84")
    exit()

# 2. OPEN WEBCAM
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW fixes lag on Windows

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print("Webcam Started")
print("Press 'c' to Capture Photo | Press 'q' to Quit")

while True:
    # Read a video frame
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 3. CONVERT TO GRAYSCALE - Haar Cascade needs grayscale to work faster
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 4. FACE DETECTION USING HAAR CASCADE
    # detectMultiScale finds faces of different sizes in the image
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # 5. DISPLAY STATUS AND DRAW BOUNDING BOX
    status_text = "Face Not Detected"
    color = (0, 0, 255) # Red

    if len(faces) > 0:
        status_text = "Face Detected"
        color = (0, 255, 0) # Green
        
        # Draw rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # Put text on the video feed
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, "Press 'c' to Capture | 'q' to Quit", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 6. SHOW THE LIVE VIDEO FEED
    cv2.imshow("Face Detection - Online Exam", frame)

    # 7. KEY PRESSES
    key = cv2.waitKey(1) & 0xFF

    # Press 'c' to capture and save image
    if key == ord('c'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(PHOTO_FOLDER, f"capture_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Image Saved Successfully: {filename}")

    # Press 'q' to quit
    elif key == ord('q'):
        print("Exiting...")
        break

# Release webcam and close windows
cam.release()
cv2.destroyAllWindows()