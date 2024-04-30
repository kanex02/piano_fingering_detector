# - - - - - - - - - - - - - - - - - - - - - - - - - 
# piano.py:  Main file to run to play the piano program
# - - - - - - - - - - - - - - - - - - - - - - - - -
import itertools
import numpy as np
import cv2
from fiducial import *
from fingers import *
from merged_hough import *
from pygame import midi
import os

IMAGE_LOCATION = 'predictions/original.jpg'
MIDI_KEY_DOWN = 0x90
MIDI_BLACK_KEYS = [82, 80, 78, 75, 73, 70, 68, 66, 63, 61, 58, 56, 54, 51, 49, 46, 44, 42, 39, 37]
MIDI_WHITE_KEYS = [84, 83, 81, 79, 77, 76, 74, 72, 71, 69, 67, 65, 64, 62, 60, 59, 57, 55, 53, 52, 50, 48, 47, 45, 43,
                   41, 40, 38, 36]
C_MAJOR_FINGERING = [(60, 5), (62, 6), (64, 7), (65, 5), (67, 6), (69, 7), (71, 8), (72, 9)]
MIDI_TO_NOTES = {
    36: 'C2',
    37: 'C#/Db2',
    38: 'D2',
    39: 'D#/Eb2',
    40: 'E2',
    41: 'F2',
    42: 'F#/Gb2',
    43: 'G2',
    44: 'G#/Ab2',
    45: 'A2',
    46: 'A#/Bb2',
    47: 'B2',
    48: 'C3',
    49: 'C#/Db3',
    50: 'D3',
    51: 'D#/Eb3',
    52: 'E3',
    53: 'F3',
    54: 'F#/Gb3',
    55: 'G3',
    56: 'G#/Ab3',
    57: 'A3',
    58: 'A#/Bb3',
    59: 'B3',
    60: 'C4',
    61: 'C#/Db4',
    62: 'D4',
    63: 'D#/Eb4',
    64: 'E4',
    65: 'F4',
    66: 'F#/Gb4',
    67: 'G4',
    68: 'G#/Ab4',
    69: 'A4',
    70: 'A#/Bb4',
    71: 'B4',
    72: 'C5',
    73: 'C#/Db5',
    74: 'D5',
    75: 'D#/Eb5',
    76: 'E5',
    77: 'F5',
    78: 'F#/Gb5',
    79: 'G5',
    80: 'G#/Ab5',
    81: 'A5',
    82: 'A#/Bb5',
    83: 'B5',
    84: 'C6'
}
FINGERS = {
    0: 'Left Pinky',
    1: 'Left Ring',
    2: 'Left Middle',
    3: 'Left Index',
    4: 'Left Thumb',
    5: 'Right Thumb',
    6: 'Right Index',
    7: 'Right Middle',
    8: 'Right Ring',
    9: 'Right Pinky',
}


def main():
    print(os.getcwd())
    if not os.path.exists("predictions"):
        os.mkdir("predictions")

    # take_reference_image("predictions/original.jpg")

    # - - - - - - - - - Find fiducial location - - - - - - - - - - - - - - - - - -
    img = cv2.imread("predictions/original.jpg")
    top, bottom = fiducial_detect(img)
    img[0:top - 20, 0:] = list(itertools.repeat(list(itertools.repeat([0, 0, 0], len(img[0]))), top - 20))
    img[bottom:1080, 0:] = list(itertools.repeat(list(itertools.repeat([0, 0, 0], len(img[0]))), 1080-bottom))
    cv2.imwrite("predictions/cropped.jpg", img)
    # #
    # return

    # - - - - - - Contrast - - - - - - - - - - - - - - - - - - - - - - - - - - -

    img = cv2.imread("predictions/cropped.jpg")
    img = cv2.blur(img, (20, 5))
    img = cv2.addWeighted(img, 10, img, 0, -1500)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('predictions/contrast.jpg', img)

    # return

    # - - - - - - Canny - - - - - - - - - - - - - - - - -
    img = cv2.imread('predictions/contrast.jpg')

    edges = cv2.Canny(img, threshold1=80, threshold2=130)
    cv2.imwrite('predictions/canny.jpg', edges)  # Save the image Canny Edge Detection as an image

    # - - - - - - - - Hough - - -

    merged_lines_x = hough_merged_image(edges, 9, 10, 35, 10)

    img = cv2.imread('predictions/cropped.jpg')

    for line in merged_lines_x:
        cv2.line(img, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (0, 0, 255), 2)

    cv2.imwrite('predictions/hough.jpg', img)

    # - - - - - - - - - - - - - Merge - - - - - - - - - - - - - - - -

    img = cv2.imread('predictions/cropped.jpg')
    merge_close(merged_lines_x, 30, 1)
    for line in merged_lines_x:
        cv2.line(img, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (0, 0, 255), 2)
    cv2.imwrite('predictions/merged.jpg', img)

    # - - - - - - Find longest horizontal lines for keyboard edges - - - - - - - -
    horizontals = []
    threshold_size = 200  # size threshold to determine if line is long enough

    for line in merged_lines_x:
        if top < line[0][1] < bottom-40 and top < line[1][1] < bottom-40:
            if abs(line[0][0] - line[1][0]) > threshold_size:
                horizontals.append(sorted(line))

    ed = sorted(horizontals, key=lambda x: (x[0][0]-x[1][0])**2 + (x[0][1]-x[1][1]) ** 2, reverse=True)  # sort by length

    p = cv2.imread('predictions/cropped.jpg')
    for e in ed[0:2]:
        e.sort()
        cv2.line(p, e[0], e[1], (255, 0, 0), 2)
    cv2.imwrite('predictions/selected_lines.jpg', p)  # draw longest two lines onto image and save

    ed.sort(key=lambda x: x[0][1])

    # Elongate top line since the keyboard is a little rounded
    ed[0][0] = (ed[0][0][0]-10, ed[0][0][1])
    ed[0][1] = (ed[0][1][0]+10, ed[0][1][1])

    # Corners of keyboard taken from the reference image
    vert = [(0, 0)] * 4
    vert[0] = ed[0][0]
    vert[1] = ed[0][1]
    vert[2] = ed[1][1]
    vert[3] = ed[1][0]
    vert = np.float32(vert)

    # Corners of output
    height, width = p.shape[:2]
    outs = np.float32([(0, 0), (width, 0), (width, height), (0, height)])

    # # - - - - - - - - - - - - Perspective Transform - - - - - - - - - - - - - - - - - - -
    perspective_image = cv2.imread("predictions/original.jpg")
    M = cv2.getPerspectiveTransform(vert, outs)
    out = cv2.warpPerspective(perspective_image, M, (width, height))
    cv2.imwrite('predictions/transformed.jpg', out)  # save perspective transform image

    # # - - - - - - - - - - - Draw on key segmentation - - - - - - - - - - - - - - - - - -
    perspective_keys = out.copy()

    black_key_base_coord = 380  # coordinate of base of black keys

    space = 27  # distance from white key to black key
    extra_y = 14  # extra distance when two white keys together
    key = 50  # distance from white key to white key

    spaces = np.array(
        [
            90,
            key, space, key, space, key, 2 * space + extra_y, key, space, key,
                                         2 * space + extra_y,
            key, space, key, space, key, 2 * space + extra_y, key, space, key,
                                         2 * space + extra_y,
            key, space, key, space, key, 2 * space + extra_y, key, space, key,
                                         2 * space + extra_y,
            key, space, key, space, key, 2 * space + extra_y, key, space, key,
        ]
    )  # distance array
    black_keys = []
    total = 0
    i = 0
    while i < len(spaces):
        key = [total := total + spaces[i], total := total + spaces[i + 1]]
        black_keys.append(key)
        i += 2

    white_note_borders = np.linspace(0, width, num=30)
    draw_white_keys(black_key_base_coord, height, perspective_keys, white_note_borders)
    draw_black_keys(black_key_base_coord, height, perspective_keys, black_keys)

    cv2.imwrite('predictions/transformed_withlines.jpg', perspective_keys)  # saves drawn on lines

    # # - - - - - - - - - - - Start of main function to run in real-time  - - - - - - - - - - - - - -

    cap = cv2.VideoCapture(0)  # Open the first camera connected to the computer.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    try:
        camera_matrix = np.loadtxt('./camera_matrix.npy')
        distortion_coeff = np.loadtxt('./distortion_coeff.npy')
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeff, (w, h), 1, (w, h))
    except:
        raise FileExistsError("Missing Camera Matrices and Distortion Files.")

    hand_tracker = HandTracker()

    midi.init()
    midi_input = midi.Input(midi.get_default_input_id())
    output = []

    while True:

        success, new_img = cap.read()
        new_img = cv2.undistort(new_img, camera_matrix, distortion_coeff, None, new_camera_matrix)
        height, width = new_img.shape[:2]

        warped = cv2.warpPerspective(new_img, M, (width, height))
        draw_white_keys(black_key_base_coord, height, warped, white_note_borders)
        draw_black_keys(black_key_base_coord, height, warped, black_keys)

        if midi_input.poll():
            event = midi_input.read(1)
            if event[0][0][0] == MIDI_KEY_DOWN:

                # Find location of fingertips in np arrays
                fingers = hand_tracker.fingers_find(new_img, width, height)

                finger_points = tuple(map(lambda point: finger_transform(M, point), fingers))

                for point in finger_points:
                    cv2.circle(warped, point, 3, (0, 0, 255), 6)

                key = event[0][0][1]
                fingers_on_note = []
                if key in MIDI_BLACK_KEYS:
                    i = MIDI_BLACK_KEYS.index(key)
                    border = black_keys[i]
                    for finger, coord in enumerate(finger_points):
                        if coord[1] > black_key_base_coord and border[0] < coord[0] < border[1]:
                            fingers_on_note.append((finger, coord))
                else:
                    i = MIDI_WHITE_KEYS.index(key)
                    border = [white_note_borders[i], white_note_borders[i + 1]]
                    for finger, coord in enumerate(finger_points):
                        if (coord[1] < black_key_base_coord or not is_black_note(coord, black_keys, -5)) \
                                and (border[0] < coord[0] < border[1]):
                            fingers_on_note.append((finger, coord))

                note_name = MIDI_TO_NOTES[key]
                if fingers_on_note:
                    finger_name = FINGERS[sorted(fingers_on_note, key=lambda x: x[1][1])[0][0]]
                    print(note_name, 'played with', finger_name)
                    output.append(note_name + ';' + finger_name + "\n")
                else:
                    print(note_name, 'MISSED')
                    output.append(note_name + ';missed\n')

        scaled_down = cv2.resize(warped, (960, 540))
        cv2.imshow("Image", scaled_down)  # show current seen image from camera lens
        if cv2.waitKey(1) != -1:
            break

    file = open("output.txt", "w")
    file.writelines(output)
    file.close()


def take_reference_image(output_location):
    cap = cv2.VideoCapture(0)  # Open the first camera connected to the computer.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    try:
        camera_matrix = np.loadtxt('./camera_matrix.npy')
        distortion_coeff = np.loadtxt('./distortion_coeff.npy')
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeff, (w, h), 1, (w, h))
    except:
        raise FileExistsError("Missing Camera Matrices and Distortion Files.")
    original = None
    while cv2.waitKey(1) == -1:
        ret, frame = cap.read()
        original = cv2.undistort(frame, camera_matrix, distortion_coeff, None, new_camera_matrix)
        scaled_down = cv2.resize(original, (960, 540))
        cv2.imshow("Image", scaled_down)
    cv2.imwrite(output_location, original)
    cv2.destroyAllWindows()


def is_black_note(coord, black_notes, threshold):
    return any(border[1] - threshold < coord[0] < border[1] + threshold for border in black_notes)


def finger_transform(M, finger_point):
    finger_point = np.array([[finger_point]], dtype=np.float32)
    transform = cv2.perspectiveTransform(finger_point, M)
    x_coord = int(transform[0][0][0])
    y_coord = int(transform[0][0][1])
    coords = np.array([x_coord, y_coord])
    return coords


def draw_black_keys(black, height, keyboard, black_keys):
    for key in black_keys:
        for x in key:
            cv2.line(keyboard, (x, black), (x, height), (255, 0, 0), 2)


def draw_white_keys(black, height, keyboard, t):
    i = 0
    for num in t:
        if i in [0, 1, 5, 8, 12, 15, 19, 22, 26, 29]:
            cv2.line(keyboard, (round(num), 0), (round(num), height), (0, 0, 255), 2)
        else:
            cv2.line(keyboard, (round(num), 0), (round(num), black), (0, 0, 255), 2)
        i += 1


# RUN PROGRAM
main()
