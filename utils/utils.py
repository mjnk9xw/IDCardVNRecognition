import base64
import io
import math
import tensorflow as tf
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
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = np.array(image)
    image = rotate(image)
    return image


def image_from_base64(base64_data):
    """
    Convert base64 to image as numpy array
    :param base64_data: Image as base64 string
    :return: Image as numpy array
    """
    img = base64.b64decode(base64_data)
    with io.BytesIO(img) as b:
        img = Image.open(b)
        img = np.array(img)
        img = rotate(img)
    return img


def rotate(image):
    """
    Rotate image to vertical view
    :param image: Image as numpy array
    :return: Image is rotated as numpy array
    """
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0,
                            100, minLineLength=100, maxLineGap=30)

    angles = []

    for [[x1, y1, x2, y2]] in lines:
        # cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    if int(median_angle) == 0:
        return image
    img_rotated = ndimage.rotate(image, median_angle)

    print(f"Angle is {median_angle:.04f}")
    return img_rotated


def preprocess_image(image, target_size):
    """
    :param image: Image as numpy array need to be preprocess
    :param target_size: Size of image after preprocess
    :return: img: The image numpy array from PIL object
    :return: original_image: the image numpy array from OpenCV
    :return: original_width: width of image
    :return: original_height: height of image
    """
    original_width, original_height = image.shape[1], image.shape[0]
    original_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    img = Image.fromarray(image, mode='RGB')
    img = img.resize(target_size, resample=Image.ANTIALIAS)
    img = tf.keras.preprocessing.image.img_to_array(img) / 255.
    return img, original_image, original_width, original_height


def preprocess_aligned_image(aligned_image, target_size):
    original_height, original_width, _ = aligned_image.shape
    img = cv2.resize(aligned_image, target_size)
    img = np.float32(img / 255.)
    return img
