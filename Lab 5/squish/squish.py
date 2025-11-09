#!/usr/bin/env python3
# Single-file version: Hand + Face detection + Squish effect
# No sound or volume control

import cv2
import time
import numpy as np
import math
import mediapipe as mp

#########################
# Initialize
#########################

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#########################
# Mediapipe hand tracking setup
#########################

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def find_hands(img, draw=True):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if draw:
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
    return img, results

def find_positions(results, img):
    lm_list = []
    if results.multi_hand_landmarks:
        my_hand = results.multi_hand_landmarks[0]
        for id, lm in enumerate(my_hand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append([id, cx, cy])
    return lm_list

#########################
# Helper
#########################

def len_calc(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

#########################
# Main loop
#########################

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from camera.")
        break

    img, results = find_hands(img)
    lmList = find_positions(results, img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 6)

    # Draw faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(img, f"({x}, {y})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if len(lmList) != 0:
        thumbX, thumbY = lmList[4][1], lmList[4][2]   # Thumb tip
        pointerX, pointerY = lmList[8][1], lmList[8][2]  # Index tip
        cx, cy = (thumbX + pointerX) // 2, (thumbY + pointerY) // 2

        # Draw landmarks and line
        cv2.circle(img, (thumbX, thumbY), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (pointerX, pointerY), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (thumbX, thumbY), (pointerX, pointerY), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        # Distance between thumb and index
        length = len_calc(thumbX, thumbY, pointerX, pointerY)

        # Squish face if between fingers
        for (x, y, w, h) in faces:
            margin = 10
            inside = (x - margin < pointerX < x + w + margin) and (x - margin < thumbX < x + w + margin)

            if inside:
                cv2.putText(img, 'FACE BETWEEN FINGERS!', (40, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                face_roi = img[y:y+h, x:x+w]
                squish_factor = np.interp(length, [50, 300], [0.4, 1.0])
                new_w = int(w * (1 / squish_factor))
                new_h = int(h * squish_factor)
                squished = cv2.resize(face_roi, (new_w, new_h))

                # Adjust size mismatch if necessary
                squished = squished[:h, :w]
                if squished.shape[:2] != (h, w):
                    squished = cv2.resize(squished, (w, h))

                img[y:y+h, x:x+w] = squished

        # Visual cue for pinch
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # FPS counter
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
