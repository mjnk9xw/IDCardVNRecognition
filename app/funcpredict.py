import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import time
from PIL import Image
from reader.readerid import  detectorid
from reader.reader import  Predictor
from vietocr.tool.config import Cfg
from app import cccd, cmnd
import numpy

"""
=========================
== Reader model
=========================
"""
config = Cfg.load_config_from_name('vgg_transformer')
# config['weights'] = './models/reader/transformerocr_best.pth'
# config['weights'] = 'https://drive.google.com/uc?export=download&id=1-olev206xLgXYf7rnwHrcZLxxLg5rs0p'
config['weights'] = 'https://drive.google.com/uc?export=download&id=1-olev206xLgXYf7rnwHrcZLxxLg5rs0p'
config['device'] = 'cuda:0'
# self.device = device
config['predictor']['beamsearch'] = False
reader = Predictor(config)


def printInfo(info_images):
    """
    =====================================
    ==== Reader infors from infors image
    =====================================
    """
    keys = list(info_images.keys())
    try:
        keys.remove("chan_dung")
    except Exception as e:
        print("Can not chan dung error = ",e)
        return

    infors = dict()

    for key in keys:
        infors[key] = list()
        info_image = info_images[key]
        for i in range(len(info_image)):
            img = info_image[i]['image']
            if key == "id":
                imgid = Image.fromarray(numpy.uint8(img))
                s = detectorid.predict(imgid)
                idstr = str([i for i in s.split() if i.isdigit()])
                infors[key] = idstr
            elif key == "full_name" or key == "noi_thuong_tru" or key == "que_quan":
                imgid = Image.fromarray(numpy.uint8(img))
                s = detectorid.predict(imgid)
                infors[key].append(s)
            else:
                s = reader.predict(img)
                infors[key].append(s)
                # imgid = Image.fromarray(numpy.uint8(img))
                # s = detectorid.predict(imgid)
                # infors[key].append(s)
                
    que_quan_0 = infors['que_quan'][0]
    que_quan_1 = ''
    noi_thuong_tru_0 = infors['noi_thuong_tru'][0]
    noi_thuong_tru_1 = ''
    if len(infors['que_quan']) == 2:
        que_quan_1 = infors['que_quan'][1]
    if len(infors['noi_thuong_tru']) == 2:
        noi_thuong_tru_1 = infors['noi_thuong_tru'][1]        

    try:
        # print("id: " + infors['id'].replace(" ",""))
        # print("name: " + infors['full_name'][0])
        # print("date_of_birth: " + infors['date_of_birth'][0])
        # print("que_quan_0: " + que_quan_0)
        # print("que_quan_1: " + que_quan_1)
        # print("noi_thuong_tru_0: " + noi_thuong_tru_0)
        # print("noi_thuong_tru_1: " + noi_thuong_tru_1)
        print("id: " + infors['id'])
        print("name: " + infors['full_name'][0])
        print("date_of_birth: " + infors['date_of_birth'][0])
        print("que_quan_0: " + que_quan_0)
        print("que_quan_1: " + que_quan_1)
        print("noi_thuong_tru_0: " + noi_thuong_tru_0)
        print("noi_thuong_tru_1: " + noi_thuong_tru_1)
    except Exception as e:
        print("Can full info error = ",e)
        return

def predict(filename):
    print("===========================================")
    start = time.time()
    channel = grpc.insecure_channel("localhost:8500")
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    
    start = time.time()

    cccd_result = cccd.predictcccd(channel,stub, filename)
    if 'id' in cccd_result and 'full_name' in cccd_result:
        printInfo(cccd_result)
    else:
        print("check image is cmnd")
        cmnd_result = cmnd.predictcmnd(channel,stub, filename)
        if 'id' in cmnd_result:
            printInfo(cmnd_result)
        else:
            print("Not detect image")

    print("total_time:{}".format(time.time()-start))