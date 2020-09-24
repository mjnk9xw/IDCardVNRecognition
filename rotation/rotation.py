import numpy as np
import cv2
import math
from scipy import ndimage


def rotate(path):
  img_origin = cv2.imread(path)

  img_gray = cv2.cvtColor(img_origin, cv2.COLOR_BGR2GRAY)
  img_edges = cv2.Canny(img_gray, 100, 255, apertureSize=3)
  lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

  # print(lines)
  angles = []

  for [[x1, y1, x2, y2]] in lines:
      angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
      angles.append(angle)

  median_angle = np.median(angles)
  img_rotated = ndimage.rotate(img_origin, median_angle)

  print(f"Angle is {median_angle:.04f}")
  cv2.imwrite(path, img_rotated)

  return img_rotated