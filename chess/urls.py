from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^push/$', views.pushPlayers, name='pushPlayers'),
    url(r'^pushed/$', views.pushed, name='pushed'),
    url(r'^start/$', views.startCompetition, name='startCompetition'),
    url(r'^competition/table/(?P<pk>[0-9]+)/$', views.pushResult, name='pushResult'),
    url(r'^competition/round/(?P<pk>[0-9]+)/$', views.addRound, name='addRound'),

]
