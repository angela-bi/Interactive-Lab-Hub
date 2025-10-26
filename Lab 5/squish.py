# created by chatGPT, edited by hand. Chatlog: https://chatgpt.com/share/68fe61df-9890-800d-9c6a-59bfbc96a6d9

import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import subprocess

def set_volume(percent):
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(percent)}%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def play_audio():
    command = ['./loop_audio.sh']
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('Looping audio playback - press q to quit')
    return process

# Initialize volume
set_volume(50)
audio_process = play_audio()

################################
wCam, hCam = 640, 480
################################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(detectionCon=int(0.7))
minVol, maxVol = 0, 100
vol = volBar = volPer = 0

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def len_calc(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 6)

    # Draw faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(img, str(x) + ' ' + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    if len(lmList) != 0:
        thumbX, thumbY = lmList[4][1], lmList[4][2]   # Thumb tip
        pointerX, pointerY = lmList[8][1], lmList[8][2]  # Index tip

        middleX, middleY = lmList[12][1], lmList[12][2]
        ringX, ringY = lmList[16][1], lmList[16][2]
        pinkyX, pinkyY = lmList[20][1], lmList[20][2]
        cx, cy = (thumbX + pointerX) // 2, (thumbY + pointerY) // 2

        # Draw landmarks
        for x, y in [(thumbX, thumbY), (pointerX, pointerY), (middleX, middleY),
                     (ringX, ringY), (pinkyX, pinkyY)]:
            cv2.circle(img, (x, y), 15, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (thumbX, thumbY), (pointerX, pointerY), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Compute distances
        length = len_calc(thumbX, thumbY, pointerX, pointerY)
        length1 = len_calc(pointerX, pointerY, middleX, middleY)
        length2 = len_calc(middleX, middleY, ringX, ringY)
        length3 = len_calc(ringX, ringY, pinkyX, pinkyY)
        length4 = len_calc(thumbX, thumbY, ringX, ringY)

        # tracking length between thumb and index length to percentage
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        set_volume(int(vol))

        # if the face rectangle is between the thumb and pointer line
        # thumb_pointer_line = (thumbX, thumbY)----(pointerX, pointerY)
        # face_rectangle = (x, y), (x+w, y+h)

        for (x, y, w, h) in faces:
            margin = 10
            condition = (x < pointerX and pointerX < x+w) and (pointerY < y) and (x < thumbX and thumbX < x+w) and (thumbY > y+h)
            condition_with_margin = (x-margin < pointerX and pointerX < x+w+margin) and (x-margin < thumbX and thumbX < x+w+margin)

            if condition_with_margin:
                cv2.putText(img, 'FACE BETWEEN FINGERS!', (40, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                
                #### used chatGPT response as reference
                face_roi = img[y:y+h, x:x+w]
                squish_factor = np.interp(length, [50, 300], [0.4, 1.0])
                new_w = int(w * (1 / squish_factor))
                new_h = int(h * squish_factor)
                squished = cv2.resize(face_roi, (new_w, new_h))

                if squished.shape[0] > h:  # too tall
                    start_y = (squished.shape[0] - h) // 2
                    squished = squished[start_y:start_y + h, :]
                elif squished.shape[0] < h:  # too short
                    pad_y = (h - squished.shape[0]) // 2
                    squished = cv2.copyMakeBorder(squished, pad_y, h - squished.shape[0] - pad_y, 0, 0, cv2.BORDER_REPLICATE)

                if squished.shape[1] > w:  # too wide
                    start_x = (squished.shape[1] - w) // 2
                    squished = squished[:, start_x:start_x + w]
                elif squished.shape[1] < w:  # too narrow
                    pad_x = (w - squished.shape[1]) // 2
                    squished = cv2.copyMakeBorder(squished, 0, 0, pad_x, w - squished.shape[1] - pad_x, cv2.BORDER_REPLICATE)

                # Guarantee exact shape match before replacement
                squished = squished[:h, :w]

                img[y:y+h, x:x+w] = squished
                ####

                # cv2.circle(img, (face_center_x, face_center_y), 10, (0, 255, 0), cv2.FILLED)

        # Visual cue for pinch
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        audio_process.terminate()
        break

cap.release()
cv2.destroyAllWindows()
