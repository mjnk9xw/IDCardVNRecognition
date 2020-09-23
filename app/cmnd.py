from app import app

from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

from cropper.cropper import Cropper
from detector.detector import Detector
from core.utils import preprocess_image, draw_bbox
import tensorflow as tf
import cv2
import grpc
import numpy as np
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from PIL import Image

def reorient_image(im):
    im = Image.open(im)
    try:
        image_exif = im._getexif()
        image_orientation = image_exif[274]
        print(image_orientation)
        if image_orientation in (2, '2'):
            return im.transpose(Image.FLIP_LEFT_RIGHT)
        elif image_orientation in (3, '3'):
            return im.transpose(Image.ROTATE_180)
        elif image_orientation in (4, '4'):
            return im.transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (5, '5'):
            return im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (6, '6'):
            return im.transpose(Image.ROTATE_270)
        elif image_orientation in (7, '7'):
            return im.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (8, '8'):
            return im.transpose(Image.ROTATE_90)
        else:
            return im
    except (KeyError, AttributeError, TypeError, IndexError):
        return im

def predictcmnd(channel, stub, filename):

    # check cccd
    """
    =========================================
    ===== Crop and align id card image
    =========================================
    """
    request = predict_pb2.PredictRequest()
    # model_name
    request.model_spec.name = "cropper_cmnd_model"
    # signature name, default is 'serving_default'
    request.model_spec.signature_name = "serving_default"
    filepath = app.config["IMAGE_UPLOADS"]+"/"+filename
    # preprocess image
    img, original_image, original_width, original_height = preprocess_image(filepath, Cropper.TARGET_SIZE)
    if img.ndim == 3:
        img = np.expand_dims(img, axis=0)
    # request to cropper model
    request.inputs["input_1"].CopyFrom(tf.make_tensor_proto(img, dtype=np.float32, shape=img.shape))
    try:
        result = stub.Predict(request, 10.0)
        result = result.outputs["tf_op_layer_concat_14"].float_val
        result = np.array(result).reshape((-1, 9))

    except Exception as e:
        print(e)

    cropper = Cropper()
    cropper.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)

    # respone to client if image is invalid
    if cropper.respone_client(threshold_idcard=0.8) == -1:
        return
    elif cropper.respone_client(threshold_idcard=0.8) == 0:
        print("no cropper")
        cv2.imwrite('app/static/aligned_images/' + filename, original_image)
        aligned_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    else:
        print("cropper image")
        cropper.set_image(original_image=original_image)

        # output of cropper part
        aligned_image = getattr(cropper, "image_output")
        cv2.imwrite('app/static/aligned_images/' + filename, aligned_image)
        aligned_image = cv2.cvtColor(aligned_image, cv2.COLOR_BGR2RGB)

    """
    ===========================================
    ==== Detect informations in aligned image
    ===========================================
    """
    # preprocess aligned image
    original_height, original_width, _ = aligned_image.shape
    img = cv2.resize(aligned_image, Detector.TARGET_SIZE)
    img = np.float32(img/255.)
    # model_name
    request.model_spec.name = "detector_cmnd_model"
    # signature name, default is 'serving_default'
    request.model_spec.signature_name = "serving_default"

    if img.ndim == 3:
        img = np.expand_dims(img, axis=0)
    # new request to detector model
    request.inputs["input_1"].CopyFrom(tf.make_tensor_proto(img, dtype=np.float32, shape=img.shape))

    try:
        result = stub.Predict(request, 10.0)
        result = result.outputs["tf_op_layer_concat_14"].float_val
        result = np.array(result).reshape((-1, 13))

    except Exception as e:
        print(e)
    
    detector = Detector()
    detector.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)
    detector.set_info_images(original_image=aligned_image)
    # output of detector part
    info_images = getattr(detector, "info_images")
    return info_images
