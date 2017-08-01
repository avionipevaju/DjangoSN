from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from mynetwork import views

urlpatterns = [
    url(r'^index/$', views.Home.as_view(),name='index'),
    url(r'^login/$',views.Login.as_view()),
    url(r'^signup/$',views.Signup.as_view()),
    url(r'^dashboard/$',views.Dashboard.as_view(),name='dashboard'),
    url(r'^profile/$',views.Profile.as_view(),name='profile'),
    url(r'create/$',views.CreatePost.as_view()),
    url(r'^$', views.Home.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)