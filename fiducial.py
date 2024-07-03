# - - - - - - - - - - - - - - - - - - - - - - - - - 
# fiducial.py:  Function to detect the fiducial marker and return
#              the bottom right coordinate of the marker
# - - - - - - - - - - - - - - - - - - - - - - - - - 

import cv2


# fiducial_detect: Detects the fiducial marker and returns the bottom right coordinate of the marker
def fiducial_detect(image):
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
    arucoParams = cv2.aruco.DetectorParameters()
    arucoDetector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
    (corners, ids, rejected) = arucoDetector.detectMarkers(image)

    if len(corners) != 2:
        print(corners)
        raise Exception

    corners = [corner for marker in corners for corner in marker[0]]

    min_y = int(min(corner[1] for corner in corners))
    max_y = int(max(corner[1] for corner in corners))

    return min_y, max_y
