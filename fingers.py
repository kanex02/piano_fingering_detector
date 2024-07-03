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

    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

    def find_key_points(self, img):
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
        self.find_hands(img)
        leftHand, rightHand = self.find_key_points(img)
        left_hand_locations = [20, 16, 12, 8, 4]
        right_hand_locations = [4, 8, 12, 16, 20]
        fingers = [[0, 0]] * 10

        # Find the coordinate of the left index finger
        if len(leftHand) != 0:
            for i, location in enumerate(left_hand_locations):
                fingers[i] = [(round(leftHand[location][1] * width)), (round(leftHand[location][2] * height))]

        # Find the coordinate of the right index finger
        if len(rightHand) != 0:
            for i, location in enumerate(right_hand_locations):
                fingers[5 + i] = [(round(rightHand[location][1] * width)), (round(rightHand[location][2] * height))]

        return fingers
