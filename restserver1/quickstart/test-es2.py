
import json

from elasticsearch import Elasticsearch

es_client = Elasticsearch()
#res = es_client.get(index="rancidity", doc_type="Sensors", id="2018-05-18T03:02:48.114470")
chart = es_client.search(index="rancidity", doc_type="Practical",
                         body={
                             "query": {
                                 "bool": {
                                     "must": [
                                         {
                                             "match": {
                                                 "station": "8472070FFDA1"
                                             }
                                         },
                                         {
                                             "range": {
                                                 "submit_date": {
                                                     "gte": "2018-05-09 00:00:00",
                                                     "lte": "now"
                                                 }
                                             }
                                         }
                                     ]
                                 }
                             }
                         })

datelist=[]
tpmlist = []
for x in range(len(chart["hits"]["hits"])):
    datelist.append(chart["hits"]["hits"][x]["_source"]["submit_date"].split(' ')[0])
    tpmlist.append(chart["hits"]["hits"][x]["_source"]["tpm"])


print(datelist)