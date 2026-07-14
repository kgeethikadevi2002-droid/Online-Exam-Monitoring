import cv2
import os

PHOTO_FOLDER = "photos"
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(FACE_CASCADE_PATH)

def capture_photo(candidate_id):
    # Check if cascade loaded
    if FACE_CASCADE.empty():
        return None, f"ERROR: Cascade not found at {FACE_CASCADE_PATH}. Install opencv-contrib-python==4.10.0.84"
    
    if not os.path.exists(PHOTO_FOLDER):
        os.makedirs(PHOTO_FOLDER)
    
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        return None, "ERROR: Webcam not found"
        
    print("Press 's' to save photo when face is detected, 'q' to quit")
    while True:
        ret, frame = cam.read()
        if not ret: 
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow(f"Capturing for {candidate_id}", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and len(faces) > 0:
            photo_path = os.path.join(PHOTO_FOLDER, f"{candidate_id}.jpg")
            cv2.imwrite(photo_path, frame)
            cam.release()
            cv2.destroyAllWindows()
            return photo_path, "Photo captured successfully"
        elif key == ord('q'):
            cam.release()
            cv2.destroyAllWindows()
            return None, "Capture cancelled by user"
    
    cam.release()
    cv2.destroyAllWindows()
    return None, "Unknown error"