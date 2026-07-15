import cv2
import time

# 1. LOAD HAAR CASCADE MODEL
# This comes with opencv. Detects frontal faces
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)

# 2. OPEN WEBCAM
cam = cv2.VideoCapture(0) # 0 = default camera

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print("Monitoring Started... Press 'q' to Quit")

while True:
    # 3. READ FRAME FROM WEBCAM
    ret, frame = cam.read()
    if not ret:
        break

    # 4. CONVERT TO GRAYSCALE - Haar needs grayscale to work fast
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 5. DETECT FACES
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # 6. CHECK STATUS AND DISPLAY
    if len(faces) > 0:
        status = "Face Detected"
        color = (0, 255, 0) # Green
        
        # Draw bounding box around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    else:
        status = "Face Not Detected"
        color = (0, 0, 255) # Red

    # 7. SHOW STATUS TEXT ON SCREEN
    cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, "Press 'q' to Quit", (20, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 8. SHOW LIVE VIDEO FEED
    cv2.imshow("Continuous Face Monitoring", frame)

    # 9. EXIT ON 'q' KEY
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Release camera and close window
cam.release()
cv2.destroyAllWindows()