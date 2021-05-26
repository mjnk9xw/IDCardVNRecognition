import base64
import io
import math
from PIL import Image
import cv2
import numpy as np
from scipy import ndimage


def load_image(file):
    """
    Handle loading image from file
    :param file: file system object
    :return: Image as numpy array
    """
    image = Image.open(file)
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')
    image = np.array(image)
    image = rotate(image)
    cv2.imwrite('image_out.jpg', image)
    return image


def rotate(image):
    """
    Rotate image to vertical view
    :param image: Image as numpy array
    :return: Image is rotated as numpy array
    """
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 0.8,math.pi / 180.0,
                            100, minLineLength=150, maxLineGap=25)

    angles = []

    for [[x1, y1, x2, y2]] in lines:
        print([[x1, y1, x2, y2]])
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    if int(median_angle) == 0:
        print(f"Angle is {median_angle:.04f}")
        return image
    img_rotated = ndimage.rotate(image, median_angle)

    print(f"Angle is {median_angle:.04f}")
    return img_rotated

load_image("1.jpg")