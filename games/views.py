from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from games.models import Game
from user.models import Player


@require_http_methods(["GET"])
def get_recent_awaiting(request):
    awaiting_games = Game.objects.filter(players_counter=1).all()
    json_response = [game.as_json() for game in awaiting_games]
    return JsonResponse(json_response, status=200)


@require_http_methods(["GET", "POST"])
def create_new(request):
    if request.method == "POST":
        # TODO: first player random choice
        my_player = Player.objects.create(
            user=request.user,
            owner=True,
            # first=bool(random.getrandbits(1))
            first=False
        )
        new_game = Game.objects.create(
            player_p1=my_player,
            board=Game.create_new_board(),
            players_counter=1
        )
        # new_game.check_end()
        new_game.player_p1.game_id = new_game.id
        new_game.player_p1.save()
        return JsonResponse(new_game.as_json(), status=201)
    else:
        awaiting_games = [game.as_json_without_board() for game in Game.get_awaiting_games()]
    return JsonResponse(awaiting_games, status=200, safe=False)


@require_http_methods(["GET"])
def get_detailed_info(request, id):
    game = Game.objects.filter(id=id).first()
    if game is not None:
        return JsonResponse(game.as_json(), status=200)
    else:
        return JsonResponse({}, status=404)


@require_http_methods(["POST"])
def perform_action(request, id, action):
    game = Game.objects.filter(id=id).first()
    if action == "join":
        if game is not None \
                and game.player_p2 is None:
            if game.player_p1.user == request.user:
                return JsonResponse({'error': 'You are already a player in this game.'}, status=400)
            my_player = Player.objects.create(
                user=request.user,
                first=False,
                game_id=game.id,
                owner=False
            )
            game.player_p2 = my_player
            game.players_counter += 1
            game.save()
            json_response = dict(
                game=game.as_json(),
                success=True,
            )
            return JsonResponse(json_response, status=200)
        else:
            return JsonResponse({'error': 'This game is already full.'}, status=400)
    elif action == "start":
        if game is not None and game.player_p2 is not None:
            if game.player_p1.user == request.user:
                game.player_p1.first = True
                game.player_p1.save()
            elif game.player_p2.user == request.user:
                game.player_p2.first = True
                game.player_p2.save()
            else:
                return JsonResponse({'error': 'You are not participating in this game.'}, status=400)

            game.start()
            json_response = dict(
                game=game.as_json(),
                success=True,
            )
            return JsonResponse(json_response, status=200)
    elif action == 'leave':
        if not game.is_started():
            if game.player_p1.user == request.user:
                if game.player_p2 is not None:
                    game.player_p1 = game.player_p2
                    game.player_p1.save()
                    game.player_p2.delete()
                    game.player_p2.save()
                else:
                    game.player_p1.delete()
                    game.player_p1.save()
                    game.delete()
            elif game.player_p2 is not None \
                    and game.player_p2.user == request.user:
                game.player_p2.delete()
                game.player_p2.save()
                # game.save()
            else:
                return JsonResponse({'error': 'You are not participating in this game.'}, status=400)

            json_response = dict(
                success=True,
            )
            return JsonResponse(json_response, status=200)
        else:  # game already started
            return JsonResponse({'error': 'This operation cannot be performed while game is active.'}, status=400)
    elif action == 'surrender':
        if game.player_p1.user == request.user:
            game.game_end_status = 's'
            game.end()
            game.player_p2.won = True
            game.player_p2.save()
        elif game.player_p2.user == request.user:
            game.game_end_status = 's'
            game.end()
            game.player_p1.won = True
            game.player_p1.save()
        return JsonResponse({'success': True}, status=200)

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
