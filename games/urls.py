from django.conf.urls import url
from games.views import *

urlpatterns = [
    url(r'^/(?P<id>[0-9]+)$', get_detailed_info),
    url(r'^/(?P<id>[0-9]+)/(?P<action>[\w]+)/', perform_action),
    url(r'^/{id}/moves/', get_moves_list),
    url(r'^/{id}/moves/last/', get_last_move),
    url(r'^', create_new),
]
