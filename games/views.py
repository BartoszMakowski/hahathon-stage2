from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from games.models import Game
from user.models import Player

@require_http_methods(["GET"])
def get_recent_awaiting(request):
    games = {}
    return games

@require_http_methods(["GET", "POST"])
def create_new(request):
    if request.method == "POST":
        # TODO: first player random choice
        my_player = Player.objects.create(user=request.user, first=True)
        new_game = Game.objects.create(owner=my_player, board=Game.create_new_board())
        # new_game.check_end()
        new_game.owner.game_id = new_game.id
        new_game.owner.save()
        return JsonResponse(new_game.as_json(), status=201)
    else:
        # print(Game.get_awaiting_games())
        awaiting_games = [game.as_json_without_board() for game in Game.get_awaiting_games()]
        # print(Game.get_awaiting_games())
    return JsonResponse(awaiting_games, status=200, safe=False)

@require_http_methods(["GET"])
def get_detailed_info(request, id):
    game = Game.objects.filter(id=id)
    if game is not None:
        return JsonResponse(game.as_json(), status=200)
    else:
        return JsonResponse({}, status=404)

@require_http_methods(["POST"])
def perform_action(request, id, action):
    if action == "join":
        game = Game.objects.filter(id=id)
        if game is not None and game.guest is None:
            my_player = Player.objects.create(user=request.user, first=False, game_id=game.id)
            game.guest = my_player
            game.save()
            return JsonResponse(game.as_json(), status=200)
        else:
            return JsonResponse({}, status=400)
    else:
        return JsonResponse({}, status=500)


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