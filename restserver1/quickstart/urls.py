from django.conf.urls import url
#from django.urls import urls
#from rest_framework.urlpatterns import  format_suffix_patterns
from quickstart import views
from quickstart import  assetmanagerViews

urlpatterns = [

    url(r'^$', views.input),
    url(r'^test/', views.input_practical),
    url(r'^webdb/', views.input_class),
    #url(r'^(?P<pk>[0-9]+)/$',views.bbs_detail)
    url(r'^info', views.test),
    url(r'^info', views.post),
    url(r'^inputdata/concrete', views.inputPavementConcrete),
    url(r'^inputdata', views.inputPavement),

    #url(r'^IoTTest', views.iotTest),
    url(r'^inputdata/', assetmanagerViews.input),
    url(r'^assettest/', assetmanagerViews.input)

    #url(r'^info', views.test),
    #url(r'^info', views.post_schedule),
    #url(r'^sc/$', views.post, name = 'newpost')
    #url(r'^info', views.post_schedule)
]
