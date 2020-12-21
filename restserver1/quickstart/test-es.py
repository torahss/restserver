
import json

from elasticsearch import Elasticsearch

es_client = Elasticsearch()
#res = es_client.get(index="rancidity", doc_type="Sensors", id="2018-05-18T03:02:48.114470")
docs = es_client.search(index="rancidity", doc_type="Practical",
                        body ={
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
print(json.dumps(docs, indent=1))
for x in range(len(docs['aggregations']["dates_with_holes"]['buckets'])):
    datelist.append(docs['aggregations']["dates_with_holes"]['buckets'][x]['key_as_string'].split(' ')[0])

for x in range(len(docs['aggregations']["dates_with_holes"]['buckets'])):
    tpmlist.append(docs['aggregations']["dates_with_holes"]['buckets'][x]['the_avg']['value'])
tpmlist = [0 if v is None else v for v in tpmlist]

print(datelist)
print(tpmlist)
#print(json.dumps(docs['aggregations']["dates_with_holes"]['buckets'][0]['key_as_string'], indent=1))
#print(json.dumps(docs['hits']['hits'], indent=1))
#print(json.dumps(docs['hits']['hits'].values(), indent=1))
#print(docs['hits']['hits'][0]['_source']['tpm'])
#print(json.dumps(docs,indent=1))

#print(docs['hits'])
#print(res['_source'])
#return render(request, 'html5/index.html', context)
