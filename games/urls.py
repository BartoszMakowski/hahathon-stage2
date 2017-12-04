from django.conf.urls import url
from games.views import *

urlpatterns = [
    url(r'^(?P<id>[0-9]+)$', get_detailed_info),
    url(r'^(?P<id>[0-9]+)/(?P<action>(join|start|leave|surrender))/$', perform_action),
    url(r'^(?P<id>[0-9]+)/moves/$', get_moves_or_make_move),
    url(r'^(?P<id>[0-9]+)/moves/last/$', get_last_move),
    url(r'^$', create_new_or_get_awaiting),
]
