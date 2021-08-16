from django.urls import path, re_path

from rocket.launcher import views

urlpatterns = [
    re_path('^$', views.index),
    re_path('^pad2$', views.cursorPad),
    re_path('^pad$', views.controlPad),
    re_path('^live$', views.liveStream),
    re_path('^ctrl/(?P<cmd>[0-9A-z]+)$', views.controlCommand),
    re_path('^snapshot2$', views.snapshot2),
    re_path('^snapshot$', views.snapshot),
    path('top/', views.index),
]
