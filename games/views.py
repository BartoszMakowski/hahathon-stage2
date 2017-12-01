from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_recent_awaiting(request):
    games = {}
    return games

@require_http_methods(["POST"])
def create_new(request):
    game_info = {}
    return game_info

@require_http_methods(["GET"])
def get_detailed_info(request, id):
    game_datails = {}
    return game_datails

@require_http_methods(["POST"])
def perform_action(request, id, action):
    action_status = {}
    return action_status

@require_http_methods(["GET", "POST"])
def get_moves_list(request, id):
    if request.method == "GET":
        moves_list = []
        return moves_list
    elif request.method == "POST":
        move_status = {}
        return move_status

@require_http_methods(["GET"])
def get_last_move(request, id):
    last_move = {}
    return last_move