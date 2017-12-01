from django.conf.urls import url
from games.views import *


urlpatterns = [
                  url(r'^/', create_new),
                  url(r'^/(?P<id>[0-9a-f-]+)', get_detailed_info),
                  url(r'^/(?P<id>[0-9a-f-]+)/(?P<action>[\w]+)/', perform_action),
                  url(r'^/{id}/moves/', get_moves_list),
                  url(r'^/{id}/moves/last/', get_last_move),
              ]
