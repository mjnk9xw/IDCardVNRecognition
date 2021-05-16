nohup tensorflow_model_server --port=8500 --rest_api_port=8501 --model_config_file=./models/serving.config &
sleep 5
nohup /home/mjnk9xw/anaconda3/bin/python run.py > logapi.log &