#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

## migrate from server_merge.py

from maxfw.core import MAXApp
from api import ModelMetadataAPI, ModelPredictAPI
from config import API_TITLE, API_DESC, API_VERSION
import threading
import socket
import requests
import numpy as np
import os

def socketNetwork(s = socket.socket()):
    while True:
        try:
            #Accept connections from the outside
            (clientsocket, address) = s.accept()
            clientsocket.settimeout(1.0)
            print(" - Get connection from {}".format(address))
            with open('record.wav', 'wb') as wavFile:
                while True:
                    try:
                        data = clientsocket.recv(1024)
                        if not data:
                            break
                        wavFile.write(data)
                    except socket.timeout:
                        break
        except KeyboardInterrupt:
            break
        
        print(" - Finished receiving audio file")

        # run prediction
        server_predict = run_prediction('record.wav')
            
        print(" - Finished running prediction")
        predictions = []
        for idx, i in enumerate(server_predict['predictions']):
            p = "{}:{}".format(i['label'], round(float(i['probability']), 2))
            predictions.append(p)
            print(p)
            
        if len(predictions):
            for i in predictions:
                print(" -- {}".format(i))
            output = ";".join(predictions)
        else:
            output = "unrecognized"

        print(" - Sending response back to client: {}".format(output))
        clientsocket.send(bytes(str(output), 'utf-8'))
        clientsocket.close()
        
    s.close()

def run_prediction(file_path = 'record.wav'):
    model_endpoint = 'http://localhost:5000/model/predict'
    file_path = file_path

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url = model_endpoint, files = file_form)

    assert r.status_code == 200

    response = r.json()

    assert response['status'] == 'ok'

    return response

def server_app():
    max_app = MAXApp(API_TITLE, API_DESC, API_VERSION)
    max_app.add_api(ModelMetadataAPI, '/metadata')
    max_app.add_api(ModelPredictAPI, '/predict')
    max_app.run()

def server_medium():
    s = socket.socket()
    s.bind(('', 8000))
    s.listen(3)
    socketNetwork(s)

if __name__ == "__main__":
    print(" - Start server app, port 5000")
    app = threading.Thread(target = server_app, args = ())
    app.start()
    print(" - Start server medium, port 8000")
    medium = threading.Thread(target = server_medium, args = ())
    medium.start()