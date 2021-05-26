import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import time
from PIL import Image
from vietocr.tool.config import Cfg
import numpy
from utils.utils import preprocess_image, load_image, image_from_base64
import cv2
import numpy as np
import tensorflow as tf
import yaml
from cropper.cropper import Cropper
from detector.detector import Detector
from reader.reader import Predictor

def load_config():
    """
    =========================
    == Reader model
    =========================
    """
    config = Cfg.load_config_from_name('vgg_transformer')
    config['weights'] = './models/reader/transformerocr.pth'
    # config['weights'] = 'https://drive.google.com/uc?export=download&id=1-olev206xLgXYf7rnwHrcZLxxLg5rs0p'
    # config['weights'] = 'https://drive.google.com/uc?id=13327Y1tz1ohsm5YZMyXVMPIOjoOA0OaA'
    config['device'] = 'cpu'
    # self.device = device
    config['predictor']['beamsearch'] = False
    return config

ocr_cfg = load_config()
reader = Predictor(ocr_cfg)

def build_result(file,info_images, typeKyc,start):
    keys = list(info_images.keys())
    infors = dict()
    infors['quoc_tich'] = ""
    infors['dan_toc'] = ""
    if "quoc_tich" in keys:
        info_img = info_images['quoc_tich']
        img = info_img[0]['image']
        s, acc = reader.predict(img,True)
        s = s.split(' ')[2:]
        infors['quoc_tich'] = ' '.join(s)
        if (infors['quoc_tich'] == '' or infors['quoc_tich'].replace(" ", "") == ''):
            infors['quoc_tich'] = "Việt Nam"
        keys.remove("quoc_tich")
    if "sex" in keys:
        # print(info_images['sex'])
        info_img = info_images['sex']
        img = info_img[0]['image']
        s, acc = reader.predict(img,True)
        s = s.split(' ')[-1]
        infors['sex'] = s
        keys.remove('sex')
    if "dan_toc" in keys:
        info_image = info_images["dan_toc"]
        infors["dan_toc"] = list()
        for i in range(len(info_image)):
            img = info_image[i]['image']
            s, acc = reader.predict(img,True)
            s = s.split(" ")[-1]
            infors["dan_toc"].append(s)

        keys.remove("dan_toc")

    score = 0
    total_item = 0
    for key in keys:
        # file_name= file.name()
        # file_chandung = f'./storage/{file_name}.jpg'
        if (key == 'chan_dung'):
            # opencvImage = cv2.cvtColor(np.array(info_images[key][0]['image']), cv2.COLOR_RGB2BGR)
            # cv2.imwrite(file_chandung, opencvImage)
            continue
        infors[key] = list()
        info_image = info_images[key]
        for i in range(len(info_image)):
            img = info_image[i]['image']
            s,acc = reader.predict(img,True)
            score += acc
            total_item += 1
            infors[key].append(s)
    que_quan_0 = infors['que_quan'][0]
    que_quan_1 = ''
    noi_thuong_tru_0 = infors['noi_thuong_tru'][0]
    noi_thuong_tru_1 = ''
    if len(infors['que_quan']) == 2:
        que_quan_1 = infors['que_quan'][1]
    if len(infors['noi_thuong_tru']) == 2:
        noi_thuong_tru_1 = infors['noi_thuong_tru'][1]
    result = {
        # 'urlimg': '',
        'idc': infors['id'][0].replace(" ", ""),
        'fullname': infors['full_name'][0],
        'dob': infors['date_of_birth'][0],
        'sex': infors['sex'] if 'sex' in infors else '',
        # 'ethnicity': infors['dan_toc'],
        # 'national': infors['quoc_tich'] if 'quoc_tich' in infors else 'Việt nam',
        'national': 'Việt nam',
        'country': f'{que_quan_0}, {que_quan_1}',
        'address': f'{noi_thuong_tru_0}, {noi_thuong_tru_1}',
        'score': round(score/total_item,4),
        'typekyc': typeKyc,
        'totaltime': round(time.time() - start,4)
    }
    return result

class EkycService:
    def __init__(self):
        channel = grpc.insecure_channel("localhost:8500")
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        pass

    def predict(self, file, is_base64=False):
        start = time.time()
        if is_base64:
            image = image_from_base64(file)
        else:
            image = load_image(file)
        cccd_result = self._predictcccd(image)
        if cccd_result is not None and 'id' in cccd_result and 'full_name' in cccd_result:
            return build_result(file,cccd_result, "CCCD",start)
        else:
            # print("check image is cmnd")
            cmnd_result = self.predictcmnd(image)
            if cmnd_result is not None and 'id' in cmnd_result:
                return build_result(file,cmnd_result, "CMND",start)
            else:
                # print("Not detect image")
                return {
                    # 'urlimg':"",
                    'idc': "",
                    'fullname': "",
                    'dob': "",
                    'sex': '',
                    # 'ethnicity': '',
                    'national': '',
                    'country': '',
                    'address': '',
                    'score': 0,
                    'typekyc': "None",
                    'totaltime': round(time.time() - start)
                }
    
    def _predictcccd(self, image):
        """
        =========================================
        ===== Crop and align id card image
        =========================================
        """
        result = None
        request = predict_pb2.PredictRequest()
        # model_name
        request.model_spec.name = "cropper_model"
        # signature name, default is 'serving_default'
        request.model_spec.signature_name = "serving_default"
        # preprocess image
        img, original_image, original_width, original_height = preprocess_image(image, Cropper.TARGET_SIZE)
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)
        # request to cropper model
        request.inputs["input_1"].CopyFrom(tf.make_tensor_proto(img, dtype=np.float32, shape=img.shape))
        try:
            result = self.stub.Predict(request, 10.0)
            result = result.outputs["tf_op_layer_concat_14"].float_val
            result = np.array(result).reshape((-1, 9))

        except Exception as e:
            print(e)
            return e

        cropper = Cropper()
        cropper.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)

        # respone to client if image is invalid
        if cropper.respone_client(threshold_idcard=0.8) == -1:
            return
        elif cropper.respone_client(threshold_idcard=0.8) == 0:
            # print("no cropper")
            # cv2.imwrite('app/static/aligned_images/' + filename, original_image)
            aligned_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        else:
            # print("cropper image")
            cropper.set_image(original_image=original_image)
            # output of cropper part
            aligned_image = getattr(cropper, "image_output")
            cv2.imwrite('storage/b.jpg', aligned_image)
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
        request.model_spec.name = "detector_model"
        # signature name, default is 'serving_default'
        request.model_spec.signature_name = "serving_default"

        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)
        # new request to detector model
        request.inputs["input_1"].CopyFrom(tf.make_tensor_proto(img, dtype=np.float32, shape=img.shape))

        try:
            result = self.stub.Predict(request, 10.0)
            result = result.outputs["tf_op_layer_concat_14"].float_val
            result = np.array(result).reshape((-1, 13))

        except Exception as e:
            print("Detect = ",e)
        
        detector = Detector()
        detector.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)
        detector.set_info_images(original_image=aligned_image)
        # output of detector part
        info_images = getattr(detector, "info_images")
        return info_images


    def predictcmnd(self, image):
    
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
        # preprocess image
        img, original_image, original_width, original_height = preprocess_image(image, Cropper.TARGET_SIZE)
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)
        # request to cropper model
        request.inputs["input_1"].CopyFrom(tf.make_tensor_proto(img, dtype=np.float32, shape=img.shape))
        try:
            result = self.stub.Predict(request, 10.0)
            result = result.outputs["tf_op_layer_concat_14"].float_val
            result = np.array(result).reshape((-1, 9))

        except Exception as e:
            print("Cropper cmnd = ",e)

        cropper = Cropper()
        cropper.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)

        # respone to client if image is invalid
        if cropper.respone_client(threshold_idcard=0.8) == -1:
            # print(cropper.respone_client(threshold_idcard=0.8))
            return
        elif cropper.respone_client(threshold_idcard=0.8) == 0:
            # print("no cropper")
            # cv2.imwrite('app/static/aligned_images/' + filename, original_image)
            aligned_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        else:
            # print("cropper image")
            cropper.set_image(original_image=original_image)
            # print("Cropper cmnd end")
            # output of cropper part
            aligned_image = getattr(cropper, "image_output")
            cv2.imwrite('storage/c.jpg', aligned_image)
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
            # print("Detect cmnd = ok")
            result = self.stub.Predict(request, 10.0)
            result = result.outputs["tf_op_layer_concat_14"].float_val
            result = np.array(result).reshape((-1, 13))
            # print("Detect cmnd = end")

        except Exception as e:
            print("Detect cmnd = ",e)
        
        detector = Detector()
        detector.set_best_bboxes(result, original_width=original_width, original_height=original_height, iou_threshold=0.5)
        detector.set_info_images(original_image=aligned_image)
        # output of detector part
        info_images = getattr(detector, "info_images")
        return info_images

