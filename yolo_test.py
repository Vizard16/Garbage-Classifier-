import ultralytics
import numpy as np
import cv2

# Load your YOLO model (make sure waste_classifier.pt is in the same folder)
model = ultralytics.YOLO('waste_classifier.pt')

# Warmup with a blank frame
warmupFrame = np.zeros((360, 640, 3), dtype=np.uint8)
model.predict(source=warmupFrame, verbose=False)
print("✅ Model warmed up")

state = 1
last_state = 1

# Open the default laptop camera (0 = first camera)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW helps on Windows

if not cap.isOpened():
    print("❌ Cannot access camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 360))
    results = model(frame, verbose=False)
    
    boxes = []
    confidences = []
    classids = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
            class_id = box.cls[0].item()
            prob = round(box.conf[0].item(), 2)
            if prob > 0.3:
                boxes.append([x1, y1, x2-x1, y2-y1])
                confidences.append(float(prob))
                classids.append(class_id)

    for i in range(len(boxes)):
        x, y, w, h = boxes[i]
        class_name = model.model.names[classids[i]]
        if str(class_name) == "plastic":
            state = 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        elif str(class_name) == "can":
            state = 2
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, str(confidences[i]), (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.putText(frame, str(class_name), (x, y-30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    if state != last_state:
        if state == 1:
            print("🟦 plastic detected")
        elif state == 2:
            print("🟩 can detected")
        last_state = state
    
    cv2.imshow("Waste Classifier", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
