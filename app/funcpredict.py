import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import time
from app import cccd, cmnd

def predict(filename):
    print("===========================================")
    channel = grpc.insecure_channel("localhost:8500")
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    request = predict_pb2.PredictRequest()
    # model_name
    request.model_spec.name = "cropper_cmnd_model"
    # signature name, default is 'serving_default'
    request.model_spec.signature_name = "serving_default"
    start = time.time()

    try:
        cccd.predictcccd(channel,stub, request, filename)
    except Exception as e:
        print("not cccd = ",e)  
    try:
        cmnd.predictcmnd(channel,stub, request, filename)
    except Exception as e:
        print("not cmnd = ",e) 

    print("total_time:{}".format(time.time()-start))