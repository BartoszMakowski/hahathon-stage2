from django.conf.urls import url
from user.views import *

from rest_framework import routers
router = routers.DefaultRouter()
# router.register(r'users', views.UserProfileViewSet)

urlpatterns = [
    url(r'^me/games/finished/$', get_finished_games),
    url(r'^me/games/$', get_active_awaiting_games),
    url(r'^register/$', register),
    url(r'^login/$', login_user),
    url(r'^logout/$', logout_user),
    url(r'^me/$', get_about_me),
    url(r'^(?P<id>[0-9]+)$', get_info),
]
