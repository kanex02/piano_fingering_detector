# - - - - - - - - - - - - - - - - - - - - - - - - - 
# fingers.py:  Functions to detect the fingertip locations and
#              to determine what key has been pressed from these
# - - - - - - - - - - - - - - - - - - - - - - - - - 

import cv2
import mediapipe as mp
import numpy as np
import math


# HandTracker: HandTracker class from MediaPipe Hands
#              Sourced online from: https://google.github.io/mediapipe/solutions/hands.html        
class HandTracker:
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(mode, maxHands, modelComplexity, detectionCon, trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

    def FindKeyPoints(self, img, draw=False):
        leftHand = []
        rightHand = []
        handTypes = []

        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_handedness:
                handType = hand.classification[0].label
                handTypes.append(handType)

            for index, handLms in enumerate(self.results.multi_hand_landmarks):
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if handTypes[index] == "Right":
                        # leftHand.append([id, cx, cy])
                        leftHand.append([id, lm.x, lm.y])
                    else:
                        # rightHand.append([id, cx, cy])
                        rightHand.append([id, lm.x, lm.y])

        return leftHand, rightHand

    # fingers_find: Determines and returns the location of the left and right index fingers from the current video frame
    #                       input: img - current image from the video frame
    #                       input: width - width of the image
    #                       input: height - height of the image
    def fingers_find(self, img, width, height):
        self.findHands(img)
        leftHand, rightHand = self.FindKeyPoints(img, draw=True)
        left_hand_locations = [20, 16, 12, 8, 4]
        right_hand_locations = [4, 8, 12, 16, 20]
        fingers = [[0, 0]]*10

        # Find the coordinate of the left index finger
        if len(leftHand) != 0:
            for i, location in enumerate(left_hand_locations):
                fingers[i] = [(round(leftHand[location][1] * width)), (round(leftHand[location][2] * height))]

        # Find the coordinate of the right index finger
        if len(rightHand) != 0:
            for i, location in enumerate(right_hand_locations):
                fingers[5+i] = [(round(rightHand[location][1] * width)), (round(rightHand[location][2] * height))]

        return fingers


# fingers_determine_key: Determines what key has been pressed based upon the location of the fingertip
#                       input: black - location of bottom of black keys
#                       input: x - transformed x coordinate of fingertip
#                       input: y - transformed y coordinate of fingertip
#                       input: white - white key segmentation
#                       input: calibration - calibration required between keys as frame goes on
#                       input: width - width of the frame
def fingers_determine_key(black, x, y, white, calibration, width):
    # Determine what key the finger point is in
    if (y >= black):
        if (x < round(white[7])):
            # keys 1-7 and 15-19
            if (x < round(calibration[5])):
                # keys 1-3 and 15-17
                if (x < round(calibration[2])):
                    # keys 1-2 and 15
                    if (x < round(calibration[0])):
                        f_key = 1
                    elif (x < round(calibration[1])):
                        f_key = 15
                    else:
                        f_key = 2
                else:
                    # keys 3 and 16-17
                    if (x < round(calibration[3])):
                        f_key = 16
                    elif (x < round(calibration[4])):
                        f_key = 3
                    else:
                        f_key = 17

            else:
                # keys 4-7 and 18-19
                if (x < round(calibration[7])):
                    # keys 4-5 and 18
                    if (x < round(white[4])):
                        f_key = 4
                    elif (x < round(calibration[6])):
                        f_key = 5
                    else:
                        f_key = 18
                else:
                    # keys 6-7 and 19
                    if (x < round(calibration[8])):
                        f_key = 6
                    elif (x < round(calibration[9])):
                        f_key = 19
                    else:
                        f_key = 7
        else:
            # keys 8-14 and 20-24
            if (x < round(calibration[15])):
                # keys 8-10 and 20-22
                if (x < round(calibration[12])):
                    # keys 8-9 and 20
                    if (x < round(calibration[10])):
                        f_key = 8
                    elif (x < round(calibration[11])):
                        f_key = 20
                    else:
                        f_key = 9
                else:
                    # keys 10 and 21-22
                    if (x < round(calibration[13])):
                        f_key = 21
                    elif (x < round(calibration[14])):
                        f_key = 10
                    else:
                        f_key = 22

            else:
                # keys 11-14 and 23-24
                if (x < round(calibration[17])):
                    # keys 11-12 and 23
                    if (x < round(white[11])):
                        f_key = 11
                    elif (x < round(calibration[16])):
                        f_key = 12
                    else:
                        f_key = 23
                else:
                    # keys 13-14 and 24
                    if (x < round(calibration[18])):
                        f_key = 13
                    elif (x < round(calibration[19])):
                        f_key = 24
                    else:
                        f_key = 14
    else:
        f_key = math.ceil((x * 14) / width)

    if (f_key < 0):
        f_key = 0

    return f_key
