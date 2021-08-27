"""rocket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from . import views

urlpatterns = [
    path('pad2/', views.cursorPad, name='pad2'),
    path('pad/', views.controlPad, name='pad'),
    # re_path('^ctrl/(?P<cmd>[0-9A-z]+)$', views.controlCommand),
    re_path('live/ctrl/(?P<cmd>[0-9A-z]+)$', views.controlCommand),
    path('live/', views.liveStream, name='live'),
    path('snapshot2/', views.snapshot2, name='snapshot2'),
    path('snapshot/', views.snapshot, name='snapshot'),
    path('top/', views.index, name='top'),
    path('', views.index),  # fault route
]
