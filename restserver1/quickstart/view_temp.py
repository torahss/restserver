from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from quickstart.models import SensorData
from quickstart.serializers import SensorSerializer
import json
from elasticsearch import Elasticsearch
import datetime
import certifi
import requests

from .forms import EventForm

from .models import SensorData
from django.http import HttpResponse
from django.shortcuts import redirect


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
def input(request, format=None):
    if request.method == 'POST':
        nowdate = datetime.datetime.now()
        js = json.loads(request.body.decode('utf-8'))
        js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
        js["tpm"] = int(js["tpm"], 16)
        js["temp"] = int(js["temp"], 16)
        print(js["tpm"])
        print(js["temp"])
        es_client = Elasticsearch()
        e = es_client.index(index="rancidity", doc_type="Sensors", id=nowdate,
                            body=js)

        imgUrl = ""
        contents = ""
        if (js["tpm"] >= 14 and js["tpm"] < 22):
            imgUrl = "http://clipart-library.com/images/rTjKneMgc.gif"

            contents = "TPM is %d. \n Please, check an oil" % js["tpm"]
            sendPush(imgUrl=imgUrl, contents=contents)
            print("yellow")

        elif (js["tpm"] >= 22 and js["tpm"] <= 24):
            imgUrl = "http://clipart-library.com/images/6cr5qn8Ei.png"

            contents = "TPM is %d. \n Please, change an oil" % js["tpm"]
            sendPush(imgUrl=imgUrl, contents=contents)
            print("redcheck")

        elif (js["tpm"] > 24):
            imgUrl = "http://www.freeiconspng.com/uploads/alert-icon-red-11.png"
            contents = "TPM is %d. \n Please, change an oil!!!" % js["tpm"]
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
        nowdate = datetime.datetime.now()
        js = json.loads(request.body.decode('utf-8'))
        js["submit_date"] = nowdate.strftime('%Y-%m-%d %H:%M:%S')
        js["tpm"] = int(js["tpm"], 16)
        js["temp"] = int(js["temp"], 16)
        print(js["tpm"])
        print(js["temp"])
        es_client = Elasticsearch()
        e = es_client.index(index="rancidity", doc_type="Practical", id=nowdate,
                            body=js)
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


def test(request):
    if request.method == "POST":
        form = EventForm(request.POST)

    elif request.method == 'GET':

        # now = datetime.datetime.now()
        # return render(request, 'html5/index.html', {"cd":now})
        es_client = Elasticsearch()
        res = es_client.search(index="rancidity", doc_type="Sensors",
                               body={
                                   "sort": {"submit_date": "desc"},
                                   "size": 1,
                                   'query': {
                                       'match': {
                                           'station': '8472071815CC'
                                       }
                                   }
                               })

        docs = es_client.search(index="rancidity", doc_type="Sensors",
                                body={
                                    "aggs": {
                                        "date_ranges": {
                                            "date_range": {
                                                "field": "submit_date",
                                                "ranges": [
                                                    {"from": "now-1d/d"},
                                                    {"from": "now"},
                                                    {"from": "now-1w"},
                                                    {"from": "now-1M"},
                                                    {"from": "now-3M"}
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
                                            "station": "8472071815CC"
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
                                                 }]
                                         }
                                     },
                                     "size": 1,
                                     "aggregations": {
                                         "dates_with_holes": {
                                             "date_histogram": {
                                                 "field": "submit_date",
                                                 "interval": "day",
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
        for x in range(len(chart['aggregations']["dates_with_holes"]['buckets'])):
            datelist.append(chart['aggregations']["dates_with_holes"]['buckets'][x]['key_as_string'].split(' ')[0])

        for x in range(len(chart['aggregations']["dates_with_holes"]['buckets'])):
            value = chart['aggregations']["dates_with_holes"]['buckets'][x]['the_avg']['value']
            tpmlist.append(value)
        tpmlist = [0 if v is None else v for v in tpmlist]

        # print(res['_source'])
        context = {'station': res['hits']['hits'][0]['_source']['station'],
                   'tpm': res['hits']['hits'][0]['_source']['tpm'],
                   'temp': res['hits']['hits'][0]['_source']['temp'],
                   'submit_date': res['hits']['hits'][0]['_source']['submit_date'],
                   'date_today': docs['aggregations']['date_ranges']['buckets'][4]['the_avg']['value'],
                   'date_yesterday': docs['aggregations']['date_ranges']['buckets'][3]['the_avg']['value'],
                   'date_7day': docs['aggregations']['date_ranges']['buckets'][2]['the_avg']['value'],
                   'date_30day': docs['aggregations']['date_ranges']['buckets'][1]['the_avg']['value'],
                   'date_90day': docs['aggregations']['date_ranges']['buckets'][0]['the_avg']['value'],
                   'chart_x': str(datelist),
                   'chart_y': str(tpmlist),
                   'form': form}
        return render(request, 'html5/index.html', context)


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