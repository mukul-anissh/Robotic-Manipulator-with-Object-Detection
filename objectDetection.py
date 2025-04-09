import cv2
import serial
import time
import numpy as np

arduino = serial.Serial('COM6', 9600)
time.sleep(2)

cap = cv2.VideoCapture(2)

def get_centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # RED HSV range
    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 100, 100])
    red_upper2 = np.array([179, 255, 255])

    # GREEN HSV range
    green_lower = np.array([40, 70, 70])
    green_upper = np.array([80, 255, 255])

    mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    mask_green = cv2.inRange(hsv, green_lower, green_upper)

    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    direction = 'N'

    if contours_red and contours_green:
        largest_red = max(contours_red, key=cv2.contourArea)
        largest_green = max(contours_green, key=cv2.contourArea)

        c_red = get_centroid(largest_red)
        c_green = get_centroid(largest_green)

        x1, y1, w1, h1 = cv2.boundingRect(largest_red)
        x2, y2, w2, h2 = cv2.boundingRect(largest_green)

        cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)
        cv2.putText(frame, "Manipulator Tip (Red)", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
        cv2.putText(frame, "Target Object (Green)", (x2, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if c_red and c_green:
            dx = c_green[0] - c_red[0]
            dy = c_green[1] - c_red[1]

            if abs(dx) < 30 and abs(dy) < 30:
                direction = 'C'  # Close enough
            elif abs(dx) > abs(dy):
                direction = 'R' if dx > 0 else 'L'
            else:
                direction = 'D' if dy > 0 else 'U'

        arduino.write(direction.encode())

    else:
        arduino.write(b'N')

    cv2.putText(frame, f"Direction: {direction}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    cv2.imshow("Manipulator Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

end = 'E'
arduino.write(end.encode())
cap.release()
cv2.destroyAllWindows()
