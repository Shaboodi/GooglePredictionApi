import httplib2
import json
from flask import Flask, request, redirect, Response
from googleapiclient.discovery import build
from oauth2client import client

app = Flask(__name__)
client_secret_path = "c:\\client_secret_2.json"
redirect_uri = "http://127.0.0.1:5000/authenticated"
# redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
service = None

flow = client.flow_from_clientsecrets(
    client_secret_path,
    scope=['https://www.googleapis.com/auth/prediction', 'https://www.googleapis.com/auth/devstorage.read_write'],
    redirect_uri=redirect_uri)


@app.route('/authenticated')
def authenticated():
    global service
    code = request.args.get('code')
    print(code)
    credentials = flow.step2_exchange(code)
    http_auth = credentials.authorize(httplib2.Http())
    service = build('prediction', 'v1.6', http=http_auth)
    return 'authenticated'


@app.route('/')
def authenticate():
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri, code=302)


@app.route('/listModels')
def list_models():
    trainedmodels__list = service.trainedmodels().list(project="prediction-166711").execute()
    return Response(json.dumps(trainedmodels__list), mimetype='application/json')


@app.route('/addModel')
def addModel():
    storageDataLocation = request.args.get('storageDataLocation')
    modelName = request.args.get('modelName')
    trainedmodels__list = service.trainedmodels().insert(project="prediction-166711", body={"id": modelName,
                                                                                            "storageDataLocation": storageDataLocation,
                                                                                            "modelType": "regression"}).execute()
    return Response(json.dumps(trainedmodels__list), mimetype='application/json')


@app.route('/status')
def status():
    modelName = request.args.get('modelName')
    execute = service.trainedmodels().get(project="prediction-166711", id=modelName).execute()
    return Response(json.dumps(execute), mimetype='application/json')

@app.route('/predict')
def predict():
    modelName = request.args.get('modelName')
    csvInstance = request.args.get('csvInstance')
    execute = service.trainedmodels().predict(project="prediction-166711", id=modelName, body={"input": {"csvInstance" : [csvInstance]}}).execute()
    return Response(json.dumps(execute), mimetype='application/json')

if __name__ == '__main__':
    app.run()
