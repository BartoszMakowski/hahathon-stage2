from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def register(request):
    user_info = {}
    return user_info

@require_http_methods(["POST"])
def login(request):
    user_info = {}
    return user_info

@require_http_methods(["POST"])
def logout(request):
    return 200

@require_http_methods(["GET", "PATCH"])
def get_about_me(request):
    if request.method == "GET":
        about_me = {}
        return about_me
    elif request.method == "PATCH":
        user_info = {}
        return user_info

@require_http_methods(["GET"])
def get_info(request, id):
    user_info = {}
    return user_info

@require_http_methods(["GET"])
def get_active_awaiting_games(request):
    active_games = []
    return active_games

@require_http_methods(["GET"])
def get_finished_games(request):
    finished_games = []
    return finished_games

