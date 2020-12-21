from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from quickstart.models import SensorData, EModel
from quickstart.serializers import SensorSerializer
import json
from elasticsearch import Elasticsearch
import datetime
import certifi
import requests
from quickstart.arima import arimaRun
from quickstart.svm import svmRun
from .forms import dateForm
from django.http import HttpResponseRedirect
import pandas as pd
from .models import SensorData
from django.http import HttpResponse
from django.shortcuts import redirect
from quickstart.views import sendPush

@api_view(['POST', 'GET'])
def DeleteAll():
    if(requests.GET.get('detele_btn')) :
        print('button click')
    return HttpResponse("click")


@api_view(['POST', 'GET'])
def asset_input(request, format=None):
    if request.method == 'POST':
        print(request.body.decode('utf-8'))
        msg = request.body.decode('utf-8')
        context = {'receive_msg':'post msg :' + request.body.decode('utf-8')}
        return render(request, 'html5/test.html', context)
    elif request.method == 'GET':
        context = {'receive_msg': "test page : connection success"}
        return render(request, 'html5/test.html', context)

def elsaticSearchAll(es_client) :

    res = es_client.search(index="rancidity", doc_type="Practical",
                           body={"size": 10000, "sort": [{
                               "submit_date": {
                                   "order": "desc"
                               }}
                           ],
                                 "query": {
                                     "bool": {
                                         "must": [
                                             {"match": {
                                                 "station": "8472070FFDA1"}}
                                         ],
                                         "must_not": [
                                             {"match": {
                                                 "tpm": "9999"}}
                                         ]
                                     }
                                 }})

    return res

def elasticDataInput(data,index,type) :
    es_client = Elasticsearch()
    e = es_client.index(index=index, doc_type=type, body=data)
    print("store success")
    imgUrl = ""
    contents = ""

    # if (data["tpm"] >= 14 and data["tpm"] < 22):
    #     imgUrl = "http://clipart-library.com/images/rTjKneMgc.gif"
    #
    #     contents = "TPM is %d. Level = Normal \n Please, check an oil" % js["tpm"]
    #     sendPush(imgUrl=imgUrl, contents=contents)
    #     print("yellow")

    return e

@api_view(['POST', 'GET'])
def input(request, format=None):
    if request.method == 'POST':
        e = dict()
        js = dict()
        result = dict()
        nowdate = datetime.datetime.now()
        log_msg = "message received....."
        print(log_msg)

        js = json.loads(request.body.decode('utf-8'))
        print(js)

        if "DeviceEUI" in js.keys() :
            js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
            e= elasticDataInput(js,"assetmanager","BootMsg")
            result["message_type"] = "Booting Message"
            log_msg = "result : Boot message received -> " + js["submit_date"]
            print(log_msg)

        elif "OPERATION TIME" in js.keys() :
            js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
            e= elasticDataInput(js,"assetmanager","IntervalMSG")
            result["message_type"] = "Interval Message"
            log_msg = "result : Interval message received -> " + js["submit_date"]
            print(log_msg)

        elif "E" in js.keys() :
            js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
            e= elasticDataInput(js,"assetmanager","EventMSG")
            result["message_type"] = "Event Message"
            log_msg = "result : Event message received -> " + js["submit_date"]
            print(log_msg)

        else:
            print("format error")
            print(js["submit_date"])
            return Response("message format error")
            datelist = []
            tpmlist = []
            # for x in range(len(res['hits']['hits'])) :
            #     tpmValue = res['hits']['hits'][len(res['hits']['hits'])-(x+1)]['_source']['tpm']
            #     tpmlist.append(float(tpmValue)/10.00)
            #     dateValue = res['hits']['hits'][len(res['hits']['hits'])-(x+1)]['_source']['submit_date']
            #     datelist.append(dateValue)

        if (e["result"] == 'created'):
            # result = '\"result\":\"0000\"'
            result["result"] = "success"
            return Response(result)
        else:
            return Response(e)

    elif request.method == 'GET':
        return Response('get')
