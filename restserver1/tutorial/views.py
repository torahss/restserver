from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
import datetime
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
from django.http import HttpResponseRedirect
import pandas as pd
from django.shortcuts import redirect
import re


class DashBoardViewIotTest(TemplateView):
	template_name = 'html5/testIndex.html'


class NowDateOutput(TemplateView):
	template_name = 'html5/nowDate.html'

class IotpavementTest(TemplateView):
	template_name = 'html5/test.html'

class PavementButton(TemplateView):
	template_name = 'html5/button.html'


class DashBoardViewApp(TemplateView):
	template_name = 'dashboard_app.html'

class DashBoardViewAdmin(TemplateView):
	template_name = 'dashboard_admin.html'

class DashBoardViewPractical(TemplateView):
	template_name = 'dashboard_practical.html'

class DashBoardViewPractical_tpm(TemplateView):
	template_name = 'dashboard_tpm.html'

class DashBoardView_index(TemplateView):
	template_name = 'html5/index.html'

class DashBoardView_index2(TemplateView):
	template_name = 'html5/index3.html'

@api_view(['POST', 'GET'])
def deleteData(request, format=None):
	print(request.data)
	if request.method == 'GET':
		context = {"result":"data read... "}
		return render(request, 'dashboard_practical.html',context)
	elif request.method == 'POST':
		#입력된 날짜 포멧 확인
		datepattern = re.compile(r'\d+-(\d+)-(\d{2})')
		if not datepattern.match(request.data['date']) :
			context = {"result": "날짜입력형식오류 : yyyy-mm-dd 로 입력해주세요"}
			return render(request, 'dashboard_practical.html', context) #틀리면 오류메시지 출력

		es_client = Elasticsearch()
		date = request.data['date'] + ' 00:00:00'

		#입력된 날짜의 00시 이후 데이터 전부 삭제
		db_result = es_client.delete_by_query(index="assetmanager", doc_type="BootMsg",
							   body={"query":{
								   "range":{
								   "submit_date":{
									   "gte":date}
								   }}
							   })
		#삭제된 데이터 개수 확인
		if db_result['deleted'] == 0 :
			res = request.data['date'] + "에 입력된 데이터가 없음"
		else:
			res="삭제결과 : " + request.data['date'] + "에 입력된 데이터 총 " + str(db_result['deleted']) +"개 레코드 삭제"

	# last_date = datetime.datetime.strptime('2018-07-20 01:01:01','%Y-%m-%d %H:%M:%S')
		print(date)
		context = {"result":res}
		return render(request, 'dashboard_practical.html',context)