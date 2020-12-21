from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from quickstart.models import SensorData, EModel
from quickstart.serializers import SensorSerializer
import json
from elasticsearch import Elasticsearch
from datetime import timezone, timedelta
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

res_arima = []

def sendPush(imgUrl, contents):
    push = {
        "data": {
            "message": {
                "title": "TPM Alert",
                "contents": contents,
                "imgurl": imgUrl,
                "link": ""
            }
        },
        "to": "/topics/notice"
    }
    URL = "https://fcm.googleapis.com/fcm/send"
    headers = {"Content-Type": "application/json",
               "Authorization": "key=AAAAvo8YO9g:APA91bFuWmGOeTphIVktGyjEBhUjYFQ6ON-wMPa4VrHtDdbpq5_CAEW1sXHjSBwaDFmFIyMXnE6wJvoRjV8d4jBu6ibZtBNhjnzvfE0-ECrPcE6121DXtDj77fxGHSPQjhIeVZgFjB1p",
               }

    res = requests.post(URL, data=json.dumps(push), headers=headers)
    print("push message")
    print(res.content)


@api_view(['POST', 'GET'])
def inputPavement(request, format=None):
    if request.method == 'POST':
        nowdate = datetime.datetime.now(timezone.utc)
        print("test1")
        print(nowdate)
        js = json.loads(request.body.decode('utf-8'))
        temp = dict(lat=float(js['sensing']['latitude']), lon=float(js['sensing']['longitude']))
        js["datetime"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
        
        js['location'] = temp
        #print("Speed : " + float(js["sensing"]["speed"]))
        print("DateTime : " + js["datetime"])
        if(js["datetime"] == 0) :
            return Response("tpm=0")
        else :
            es_client = Elasticsearch()
            e = es_client.index(index="iotpavement", doc_type="primarytest",
                            body=js)
            return Response("0")


@api_view(['POST', 'GET'])
def inputPavementConcrete(request, format=None):
    if request.method == 'POST':
        nowdate = datetime.datetime.now(timezone.utc)
        print("conctre")
        print(nowdate)
        js = json.loads(request.body.decode('utf-8'))
        temp = dict(lat=float(js['sensing']['latitude']), lon=float(js['sensing']['longitude']))
        js["datetime"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')

        js['location'] = temp
        # print("Speed : " + float(js["sensing"]["speed"]))
        print("DateTime : " + js["datetime"])
        if (js["datetime"] == 0):
            return Response("tpm=0")
        else:
            es_client = Elasticsearch()
            e = es_client.index(index="iotpavementcite", doc_type="concretecitetest",
                                body=js)
            return Response("0")


@api_view(['POST', 'GET'])
def asset_input(request, format=None):
    if request.method == 'POST':
        print(request.body.decode('utf-8'))
        msg = request.body.decode('utf-8')
        context = {'receive_msg':'post msg :' + request.body.decode('utf-8')}
        render(request, 'html5/test.html', context)

        return Response(request.body.decode('utf-8'))

    elif request.method == 'GET':
        context = {'receive_msg': "test page : connection success"}
        return render(request, 'html5/test.html', context)


@api_view(['POST', 'GET'])
def input(request, format=None):
    if request.method == 'POST':

        nowdate = datetime.datetime.now(timezone.utc)
        print(nowdate)
        js = json.loads(request.body.decode('utf-8'))
        js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
        js["tpm"] = float(int(js["tpm"], 16))/10.0
        js["temp"] = float(int(js["temp"], 16))/10.0
        print(js["tpm"])
        print(js["temp"])
        if(js["tpm"] == 0) :
            return Response("tpm=0")
        else :
            es_client = Elasticsearch()
            e = es_client.index(index="rancidity", doc_type="Sensors", id=nowdate,
                            body=js)
            imgUrl = ""
            contents = ""
            res = es_client.search(index="rancidity", doc_type="Practical",
                                   body={"size":10000,"sort":[{
                                       "submit_date":{
                                           "order":"desc"
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
            datelist = []
            tpmlist = []


            for x in range(len(res['hits']['hits'])) :
                tpmValue = res['hits']['hits'][len(res['hits']['hits'])-(x+1)]['_source']['tpm']
                tpmlist.append(float(tpmValue)/10.00)
                dateValue = res['hits']['hits'][len(res['hits']['hits'])-(x+1)]['_source']['submit_date']
                datelist.append(dateValue)

            res_arima = arimaRun(list_tpm=tpmlist,list_date=datelist)
            nowdate = datetime.datetime.now()

            dicPredciton = {'predction':res_arima[0],'predictionMax':res_arima[1]}
            dicPredciton["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')

            e1 = es_client.index(index="prediction", doc_type="tpm_prediction", id=nowdate,
                                body=dicPredciton)

            if (js["tpm"] >= 14 and js["tpm"] < 22):
                imgUrl = "http://clipart-library.com/images/rTjKneMgc.gif"

                contents = "TPM is %d. Level = Normal \n Please, check an oil" % js["tpm"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("yellow")

            elif (js["tpm"] >= 22 and js["tpm"] <= 24):
                imgUrl = "http://clipart-library.com/images/6cr5qn8Ei.png"

                contents = "TPM is %d. Level = Bad \n Please, change an oil" % js["tpm"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("redcheck")

            elif (js["tpm"] > 24):
                imgUrl = "https://mayracanolaw.com/wp-content/uploads/2013/07/stop-symbol.png"
                contents = "TPM is %d. Level = Worst \n Please, change an oil!!!" % js["tpm"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("red")

            if (e["result"] == 'created'):
                # result = '\"result\":\"0000\"'
                result = {
                    "result": 0
                }
                return Response(result)
            else:
                return Response(e)

    elif request.method == 'GET':
        return Response('get')


@api_view(['POST', 'GET'])
def input_practical(request, format=None):
    if request.method == 'POST':
        nowdate = datetime.datetime.now(timezone.utc)
        js = json.loads(request.body.decode('utf-8'))
        js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
        print(js["submit_date"])
        js["tpm"] = int(js["tpm"], 16)
        js["temp"] = int(js["temp"], 16)
        print(js["tpm"])
        print(js["temp"])
        if(js["tpm"] == 0) :
            return ("result : tpm = 0")
        else :
            es_client = Elasticsearch()
            e = es_client.index(index="rancidity", doc_type="Practical", id=nowdate,
                                body=js)
            res = es_client.search(index="rancidity", doc_type="Practical",
                                   body={"size": 720, "sort": [{
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
            datelist = []
            tpmlist = []

            for x in range(len(res['hits']['hits'])):
                tpmValue = res['hits']['hits'][len(res['hits']['hits']) - (x + 1)]['_source']['tpm']
                tpmlist.append(float(tpmValue) / 10.00)
                dateValue = res['hits']['hits'][len(res['hits']['hits']) - (x + 1)]['_source']['submit_date']
                datelist.append(dateValue)

            res_arima = arimaRun(list_tpm=tpmlist, list_date=datelist)
            nowdate = datetime.datetime.now()

            dicPredciton = {'predction': res_arima[0], 'predictionMax': res_arima[1]}
            dicPredciton["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')

            e1 = es_client.index(index="prediction", doc_type="tpm_prediction", id=nowdate,
                                 body=dicPredciton)
            print(dicPredciton["predction"])
            if (dicPredciton["predction"] >= 14 and dicPredciton["predction"] < 22):
                imgUrl = "http://clipart-library.com/images/rTjKneMgc.gif"

                contents = "TPM is %.3f. Level = Normal \n Please, check an oil" % dicPredciton["predction"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("yellow")

            elif (dicPredciton["predction"] >= 22 and dicPredciton["predction"] <= 24):
                imgUrl = "http://clipart-library.com/images/6cr5qn8Ei.png"

                contents = "TPM is %.3f. Level = Bad \n Please, change an oil" % dicPredciton["predction"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("redcheck")

            elif (dicPredciton["predction"] > 24):
                imgUrl = "https://mayracanolaw.com/wp-content/uploads/2013/07/stop-symbol.png"
                contents = "TPM is %.3f. Level = Worst \n Please, change an oil!!!" % dicPredciton["predction"]
                sendPush(imgUrl=imgUrl, contents=contents)
                print("red")

            if (e["result"] == 'created'):
                # result = '\"result\":\"0000\"'
                result = {
                    "result": 0
                }

                return Response(result)
            else:
                return Response(e)

    elif request.method == 'GET':
        return Response('dev_get')


@api_view(['POST', 'GET'])
def input_class(request, format=None):
    if request.method == 'POST':
        post = "OK : post message -> "
        post = post + request.body.decode('utf-8')
        return Response(post)
    elif request.method == 'GET':
        return Response('ok_get')

@api_view(['POST', 'GET'])
def test(request):
    # now = datetime.datetime.now()
    # return render(request, 'html5/index.html', {"cd":now})
    es_client = Elasticsearch()
    res = es_client.search(index="rancidity", doc_type="Practical",
                           body={
                               "sort": {"submit_date": "desc"},
                               "size": 1,
                               'query': {
                                   'bool': {
                                       'must':[
                                           {'match':{
                                               "station": "8472070FFDA1"
                                           }}
                                       ],
                                       'must_not':[{
                                           'match':{
                                               'tpm':'0000'}}
                                       ]
                                   }
                               }
                           })
    res_prediction = es_client.search(index="prediction", doc_type="tpm_prediction",
                           body={
                               "sort": {"submit_date": "desc"},"size":1,
                               'query': {
                                   "match_all" :{}}
                                   })

	#last_date = datetime.datetime.strptime('2018-07-20 01:01:01','%Y-%m-%d %H:%M:%S')
    last_date = datetime.datetime.strptime(res['hits']['hits'][0]['_source']['submit_date'],'%Y-%m-%d %H:%M:%S')
    lDate = last_date +datetime.timedelta(days=-1)

    lDate_7days = last_date +datetime.timedelta(days=-7)
    lDate_30days = last_date + datetime.timedelta(days=-30)
    lDate_90days = last_date + datetime.timedelta(days=-90)

    docs = es_client.search(index="rancidity", doc_type="Practical",
                            body={
                                "aggs": {
                                    "date_ranges": {
                                        "date_range": {
                                            "field": "submit_date",
                                            "ranges": [
                                                {"from": datetime.datetime.strftime(lDate,'%Y-%m-%d %H:%M:%S')},
                                                {"from": datetime.datetime.strftime(last_date,'%Y-%m-%d %H:%M:%S')},
                                                {"from": datetime.datetime.strftime(lDate_7days,'%Y-%m-%d %H:%M:%S')},
                                                {"from": datetime.datetime.strftime(lDate_30days,'%Y-%m-%d %H:%M:%S')},
                                                {"from": datetime.datetime.strftime(lDate_90days,'%Y-%m-%d %H:%M:%S')}
                                            ]
                                        },
                                        "aggs": {
                                            "the_avg": {
                                                "avg": {
                                                    "field": "tpm",
                                                    "missing": 0
                                                }
                                            }
                                        }
                                    }
                                },
                                "query": {
                                    "match": {
                                        "station": "8472070FFDA1"
                                    }
                                }
                            })
    chart = es_client.search(index="rancidity", doc_type="Practical",
                             body={
                                 "query": {
                                     "bool": {
                                         "must": [{
                                             "match": {
                                                 "station": "8472070FFDA1"
                                             }
                                         },
                                             {
                                                 "match": {
                                                     "_type": "Practical"
                                                 }
                                             },
                                             {
                                                 "range":{
                                                     "submit_date":{
                                                         #"gte":"2018-05-01 00:00:00",
                                                         "gte":datetime.datetime.strftime(lDate,'%Y-%m-%d %H:%M:%S'),
                                                         "lte":datetime.datetime.strftime(last_date,'%Y-%m-%d %H:%M:%S'),
                                                     }
                                                 }
                                             }
                                         ]
                                     }
                                 },
                                 "size": 1,
                                 "aggregations": {
                                     "dates_with_holes": {
                                         "date_histogram": {
                                             "field": "submit_date",
                                             "interval": "5s",
                                             "min_doc_count": 0
                                         },
                                         "aggs": {
                                             "the_avg": {
                                                 "avg": {
                                                     "field": "tpm",
                                                     "missing": 0
                                                 }
                                             }
                                         }
                                     }
                                 }
                             })

    datelist = []
    tpmlist = []
    value = chart['aggregations']["dates_with_holes"]['buckets'][0]['the_avg']['value']
    for x in range(len(chart['aggregations']["dates_with_holes"]['buckets'])):
        datelist.append(chart['aggregations']["dates_with_holes"]['buckets'][x]['key_as_string'].split(' ')[0])

    for x in range(len(chart['aggregations']["dates_with_holes"]['buckets'])):
        if x==0 :
            value = chart['aggregations']["dates_with_holes"]['buckets'][0]['the_avg']['value']
            temp_tpm = value
        else :
            value = chart['aggregations']["dates_with_holes"]['buckets'][x]['the_avg']['value']
            if value == None or value == 0.0 :
                value = temp_tpm
            else :
                temp_tpm = value

        tpmlist.append(value/10.0)
    tpmlist = [0 if v is None else v for v in tpmlist]
    input_data = pd.DataFrame([res['hits']['hits'][0]['_source']['tpm'] / 10,
    docs['aggregations']['date_ranges']['buckets'][3]['the_avg']['value'] / 10.0,
    docs['aggregations']['date_ranges']['buckets'][2]['the_avg']['value'] / 10.0,
    docs['aggregations']['date_ranges']['buckets'][1]['the_avg']['value'] / 10.0])

    svmResult = svmRun(input_data)
    print(svmResult)
    # print(res['_source'])
    context = {'prediction' : res_prediction['hits']['hits'][0]['_source']['predction'],
               'predictionMax' : '{0:.3f}'.format(res_prediction['hits']['hits'][0]['_source']['predictionMax']),
               'station': res['hits']['hits'][0]['_source']['station'],
               'tpm': res['hits']['hits'][0]['_source']['tpm']/10,
               'temp': res['hits']['hits'][0]['_source']['temp']/10,
               'submit_date': res['hits']['hits'][0]['_source']['submit_date'],
               'date_today': '{0:.3f}'.format(docs['aggregations']['date_ranges']['buckets'][4]['the_avg']['value']/10.0),
               'date_yesterday': '{0:.3f}'.format(docs['aggregations']['date_ranges']['buckets'][3]['the_avg']['value']/10.0),
               'date_7day': '{0:.3f}'.format(docs['aggregations']['date_ranges']['buckets'][2]['the_avg']['value']/10.0),
               'date_30day': '{0:.3f}'.format(docs['aggregations']['date_ranges']['buckets'][1]['the_avg']['value']/10.0),
               'date_90day': '{0:.3f}'.format(docs['aggregations']['date_ranges']['buckets'][0]['the_avg']['value']/10.0),
               'chart_x': str(datelist),
               'chart_y': str(tpmlist),
               'level':svmResult}
    return render(request, 'html5/index.html', context)

def post(request):
    if request.method == "POST":
        form = dateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks')


@api_view(['POST', 'GET'])
def iotTest(request):
    return render(request, 'html5/testIndex.html')

'''
def post_schedule(request):
    if request.method == "POST":
        date1 = request.POST.get("datepicker1")
        date2 = request.POST.get("datepicker2")

        print(date1, date2)


        es_client = Elasticsearch()
        chart = es_client.search(index="rancidity", doc_type="Practical",
                                 body={
                                     "query": {
                                         "bool":{
                                             "must": [
                                                 {
                                                     "match": {
                                                         "station": "8472070FFDA1"
                                                     }
                                                 },
                                                 {
                                                     "range": {
                                                         "submit_date": {
                                                             "gte": date1,
                                                             "lte": date2
                                                         }
                                                     }
                                                 }
                                             ]
                                         }
                                     }
                                })

        datelist = []
        tpmlist = []
        for x in range(len(chart["hits"]["hits"])):
            datelist.append(chart["hits"]["hits"][x]["_source"]["submit_date"].split(' ')[0])
            tpmlist.append(chart["hits"]["hits"][x]["_source"]["tpm"])

    context = {'chart_x':str(datelist),
               'chart_y':str(tpmlist)}

    return render(request, 'html5/index.html', context)
'''
