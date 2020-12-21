"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from tutorial.views import DashBoardViewApp, DashBoardViewAdmin, DashBoardViewPractical, DashBoardViewPractical_tpm, DashBoardView_index,\
    DashBoardView_index2, DashBoardViewIotTest, deleteData, NowDateOutput, PavementButton,IotpavementTest
import tutorial
from quickstart.views import input

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^monitoringApp/', DashBoardViewApp.as_view(), name = 'dashboard_app'),
    url(r'^monitoring/', DashBoardViewAdmin.as_view(), name='dashboard_admin'),
    url(r'^nowdatetime/',NowDateOutput.as_view(), name='Now_date'),
    url(r'^button/', PavementButton.as_view(), name='Button'),
    url(r'^iotpavement/testindex', IotpavementTest.as_view(), name='IotpavementTest'),
    #assetmanager temporary view
    url(r'^assetmanager/temp/', deleteData, name='dashboard_practical'),
    url(r'^assetmanager/temp/all/', DashBoardViewPractical_tpm.as_view(), name='dashborad_tpm'),
    url(r'^assetmanager/', include('quickstart.urls')),
    #url(r'^html5', DashBoardView_index.as_view(), name='html5'),
    url(r'^main/index3', DashBoardView_index2.as_view()),
    url(r'^test/iotview', DashBoardViewIotTest.as_view()),
    url(r'^mobile/', DashBoardViewApp.as_view(), name='dashboard_app'),
    url(r'^temperature/', include('quickstart.urls')), # 1
    url(r'^iotpavement/', include('quickstart.urls')),
    url(r'^main/', include('quickstart.urls')),
    #url(r'^sc/', include('quickstart.urls'))

]
