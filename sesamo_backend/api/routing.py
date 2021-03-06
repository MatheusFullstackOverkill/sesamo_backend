from django.urls import re_path
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scan/(?P<room_name>\w+)/$', consumers.ScanConsumer),
    re_path(r'ws/panic-button/(?P<room_name>\w+)/$', consumers.PanicButtonConsumer),
]