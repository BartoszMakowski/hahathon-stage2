from django.conf.urls import url
from games.views import *


urlpatterns = [
                  url(r'^/', get_recent_awaiting),
                  url(r'^/id', get_detailed_info),
                  url(r'^/{id}/[join|start|leave|surrender]/', perform_action),
                  url(r'^/{id}/moves/', get_moves_list),
                  url(r'^/{id}/moves/last/', get_last_move),
              ]
