from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from snbot import views

urlpatterns = [
    url(r'^snbot/$', views.Bot.as_view(),name='bot'),
]

urlpatterns = format_suffix_patterns(urlpatterns)