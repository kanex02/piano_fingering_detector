# - - - - - - - - - - - - - - - - - - - - - - - - - 
# hough.py:  Functions to compute a merged Hough Line Transform
#                   where segments of lines close together are merged
#                   to form one line
#                   Sourced online from: https://stackoverflow.com/questions/45531074/how-to-merge-lines-after-houghlinesp
#                   References within the document for: 
#                       -   https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
#                       -   https://stackoverflow.com/questions/32702075/what-would-be-the-fastest-way-to-find-the-maximum-of-all-possible-distances-betw
#                       -   http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
# - - - - - - - - - - - - - - - - - - - - - - - - - 

import math
import cv2
import numpy as np


# hough_sort: Sorts the lines based on x or y direction
def hough_sort(lines, use_log=False):
    if (len(lines) == 1):
        return lines[0]

    line_i = lines[0]

    orientation_i = math.atan2((line_i[0][1] - line_i[1][1]), (line_i[0][0] - line_i[1][0]))

    points = []
    for line in lines:
        points.append(line[0])
        points.append(line[1])

    if (abs(math.degrees(orientation_i)) > 45) and abs(math.degrees(orientation_i)) < (90 + 45):

        # sort by y
        points = sorted(points, key=lambda point: point[1])

        if use_log:
            print("use y")
    else:

        # sort by x
        points = sorted(points, key=lambda point: point[0])

        if use_log:
            print("use x")

    return [points[0], points[len(points) - 1]]


# # hough_lines_close: Finds the lines closest to the current searched for line
# def hough_lines_close(line1, line2):
#     dist1 = math.hypot(line1[0][0] - line2[0][0], line1[0][0] - line2[0][1])
#     dist2 = math.hypot(line1[0][2] - line2[0][0], line1[0][3] - line2[0][1])
#     dist3 = math.hypot(line1[0][0] - line2[0][2], line1[0][0] - line2[0][3])
#     dist4 = math.hypot(line1[0][2] - line2[0][2], line1[0][3] - line2[0][3])

#     if (min(dist1,dist2,dist3,dist4) < 100):
#         return True
#     else:
#         return False

# hough_lines_magnitue: Computes the magnitude of each individual line
def hough_lines_magnitude(x1, y1, x2, y2):
    lineMagnitude = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
    return lineMagnitude


# hough_distance_pointline: Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline)
def hough_distance_pointline(px, py, x1, y1, x2, y2):
    LineMag = hough_lines_magnitude(x1, y1, x2, y2)

    if LineMag < 0.00000001:
        DistancePointLine = 9999
        return DistancePointLine

    u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
    u = u1 / (LineMag * LineMag)

    if (u < 0.00001) or (u > 1):
        ix = hough_lines_magnitude(px, py, x1, y1)
        iy = hough_lines_magnitude(px, py, x2, y2)
        if ix > iy:
            DistancePointLine = iy
        else:
            DistancePointLine = ix
    else:
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        DistancePointLine = hough_lines_magnitude(px, py, ix, iy)

    return DistancePointLine


# hough_get_distance: Gets the distance from a point to the line segment
def hough_get_distance(line1, line2):
    dist1 = hough_distance_pointline(line1[0][0], line1[0][1],
                                     line2[0][0], line2[0][1], line2[1][0], line2[1][1])
    dist2 = hough_distance_pointline(line1[1][0], line1[1][1],
                                     line2[0][0], line2[0][1], line2[1][0], line2[1][1])
    dist3 = hough_distance_pointline(line2[0][0], line2[0][1],
                                     line1[0][0], line1[0][1], line1[1][0], line1[1][1])
    dist4 = hough_distance_pointline(line2[1][0], line2[1][1],
                                     line1[0][0], line1[0][1], line1[1][0], line1[1][1])
    return min(dist1, dist2, dist3, dist4)


# hough_merge_pipeline: Creates the pipeline of all the merged lines and appends the merged lines to a list
#                         input: min - changeable for the minimum distance the segments must be apart to be merged
def hough_merge_pipeline(lines, min):
    super_lines_final = []
    super_lines = []
    min_distance_to_merge = min
    min_angle_to_merge = 10

    for line in lines:
        create_new_group = True
        group_updated = False

        for group in super_lines:
            for line2 in group:
                if hough_get_distance(line2, line) < min_distance_to_merge:
                    orientation_i = math.atan2((line[0][1] - line[1][1]), (line[0][0] - line[1][0]))
                    orientation_j = math.atan2((line2[0][1] - line2[1][1]), (line2[0][0] - line2[1][0]))

                    if int(abs(
                            abs(math.degrees(orientation_i)) - abs(math.degrees(orientation_j)))) < min_angle_to_merge:
                        group.append(line)

                        create_new_group = False
                        group_updated = True
                        break

            if group_updated:
                break

        if (create_new_group):
            new_group = []
            new_group.append(line)

            for idx, line2 in enumerate(lines):
                if hough_get_distance(line2, line) < min_distance_to_merge:
                    orientation_i = math.atan2((line[0][1] - line[1][1]), (line[0][0] - line[1][0]))
                    orientation_j = math.atan2((line2[0][1] - line2[1][1]), (line2[0][0] - line2[1][0]))

                    if int(abs(
                            abs(math.degrees(orientation_i)) - abs(math.degrees(orientation_j)))) < min_angle_to_merge:
                        new_group.append(line2)
            super_lines.append(new_group)

    for group in super_lines:
        super_lines_final.append(hough_sort(group))

    return super_lines_final


# hough_merged_image: Takes an image, converts to grayscale, finds a list of the merged Hough Lines and returns the lists of merged lines
#                       input: img - reference image to compute Hough Line Transform on
#                       input: t1 - Canny Threshold 1
#                       input: t2 - Canny Threshold 2
#                       input: g1 - Hough Line Threshold
#                       input: g2 - Hough Minimum Line Length
#                       input: g3 - Hough Maximum Line Gap
#                       input: min - Minimum distance apart for segments to be merged (input into hough_merge_pipeline)
def hough_merged_image(img, t1, t2, g1, g2, g3, min):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, threshold1=t1, threshold2=t2)
    cv2.imwrite('predictions/lines_edges.jpg', edges)  # Save the image Canny Edge Detection as an image

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=g1, minLineLength=g2, maxLineGap=g3)
    _lines = []
    for line in lines:
        for leftx, boty, rightx, topy in line:
            _lines.append([(leftx, boty), (rightx, topy)])

    merged_lines_x = flatten_and_merge(_lines, min)

    merge_close(merged_lines_x, 50, 1)

    # merged_lines_x = flatten_and_merge(merged_lines_x, min*1.1)

    return merged_lines_x  # , merged_lines_all # as merged_lines_y not required for future work


def combine(line1, line2, thresh_dist, thresh_angle):
    min_dist = math.inf
    max_dist = 0
    new_line = []
    for point1 in line1:
        for point2 in line2:
            dist = math.dist(point1, point2)
            if dist < min_dist:
                min_dist = dist
            if dist > max_dist:
                max_dist = dist
                new_line = [point1, point2]

    new_angle = abs(
        math.degrees(math.atan2((new_line[0][1] - new_line[1][1]), (new_line[0][0] - new_line[1][0]))))


    # print(new_angle)
    # print(min_dist)
    # if (180 - thresh_angle < new_angle < 180 + thresh_angle) or (-thresh_angle < new_angle < thresh_angle):
    #     print("ANGLE")
    # if min_dist < thresh_dist:
    #     print("DIST")
    # print(new_line)
    # img_merged_lines = cv2.imread('original.jpg')  # copy of reference image to find horizontal lines
    # cv2.line(img_merged_lines, (new_line[0][0], new_line[0][1]), (new_line[1][0], new_line[1][1]), (0, 255, 0), 2)
    # cv2.line(img_merged_lines, (line1[0][0], line1[0][1]), (line1[1][0], line1[1][1]), (0, 0, 255), 2)
    # cv2.line(img_merged_lines, (line2[0][0], line2[0][1]), (line2[1][0], line2[1][1]), (0, 0, 255), 2)
    # while cv2.waitKey(1) < 0:
    #     cv2.imshow("frame", cv2.resize(img_merged_lines, (960, 540)))

    if not (180 - thresh_angle < new_angle < 180 + thresh_angle) and not (-thresh_angle < new_angle < thresh_angle):
        return

    if min_dist < thresh_dist:
        return new_line


def merge_close(lines, thresh_dist, thresh_angle):
    i = 0
    while i < len(lines):
        j = i + 1
        while j < len(lines):
            line1 = lines[i]
            line2 = lines[j]
            new_line = combine(line1, line2, thresh_dist, thresh_angle)
            if new_line:
                lines.pop(j)
                lines.pop(i)
                lines.append(new_line)

                j = i + 1
            else:
                j += 1
        i += 1


def flatten_and_merge(_lines, min):
    _lines_x = []
    for line_i in _lines:
        orientation_i = math.atan2((line_i[0][1] - line_i[1][1]), (line_i[0][0] - line_i[1][0]))
        angle = abs(math.degrees(orientation_i))
        threshold_angle = 4
        if (angle < threshold_angle) or (angle > (180 - threshold_angle)):
            # print(abs(math.degrees(orientation_i)))
            _lines_x.append(line_i)
    _lines_x = sorted(_lines_x, key=lambda _line: _line[0][0])
    merged_lines_x = hough_merge_pipeline(_lines_x, min)
    return merged_lines_x
