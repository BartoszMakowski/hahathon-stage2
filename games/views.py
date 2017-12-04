from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from games.models import Game, Move
from user.models import Player
import simplejson as json


# create new game with empty board on POST
# or return awaiting games on GET
@require_http_methods(['GET', 'POST'])
def create_new_or_get_awaiting(request):
    if request.method == 'POST':
        my_player = Player.objects.create(
            user=request.user,
            owner=True,
            first=False
        )
        new_game = Game.objects.create(
            player_p1=my_player,
            board=json.dumps(Game.create_new_board()),
            players_counter=1
        )
        new_game.player_p1.game_id = new_game.id
        new_game.player_p1.save()
        return JsonResponse(new_game.as_json(), status=201)
    else:
        # only authenticated user can get list of awaiting games
        if request.user.is_authenticated():
            awaiting_games = [
                game.as_json_without_board()
                for game in Game.get_awaiting_games()
            ]
            return JsonResponse(awaiting_games, status=200, safe=False)
        else:  # unauthenticated user
            return JsonResponse(
                {'detail': 'Authentication credentials were not provided.'},
                status=403
            )


# return detailed info about given game
@require_http_methods(["GET"])
def get_detailed_info(request, id):
    game = Game.objects.filter(id=id).first()
    if game is not None:
        return JsonResponse(game.as_json(), status=200)
    else:
        return JsonResponse({'error': "Given game doesn't exist"}, status=404)


# perform given action (create/join/leave/surrender)
@require_http_methods(["POST"])
def perform_action(request, id, action):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return JsonResponse({'error': "Given game doesn't exist"}, status=404)
    elif action == "join":  # join to awaiting game
        # check if there is empty seat in given game
        if game.player_p2 is None:
            if game.player_p1.user == request.user:
                return JsonResponse(
                    {'error': 'You are already a player in this game.'},
                    status=400
                )
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
        else:  # game is full
            return JsonResponse(
                {'error': 'This game is already full.'},
                status=400
            )
    # start awaiting game
    elif action == "start":
        # check if there are 2 players in given game
        if game.player_p2 is not None:
            if game.player_p1.user == request.user:
                game.player_p1.first = True
                game.player_p1.save()
            elif game.player_p2.user == request.user:
                game.player_p2.first = True
                game.player_p2.save()
            else:
                return JsonResponse(
                    {'error': 'You are not participating in this game.'},
                    status=400
                )
            game.start()
            json_response = dict(
                game=game.as_json(),
                success=True,
            )
            return JsonResponse(json_response, status=200)
    # leave given game
    elif action == 'leave':
        # check if given game already started
        if not game.is_started():
            if game.player_p1.user == request.user:  # owner leaves the game
                # check if there are 2 players in the game
                if game.player_p2 is not None:
                    # guest is new owner
                    game.player_p1 = game.player_p2
                    game.player_p1.save()
                    game.player_p2.delete()
                    game.player_p2 = None
                    game.save()
                else:  # there is no guest in the game
                    game.player_p1.delete()
                    game.player_p1.save()
                    game.delete()
            elif game.player_p2 is not None \
                    and game.player_p2.user == request.user:
                # guest leaves the game
                game.player_p2.delete()
                game.player_p2 = None
                game.save()
            else:
                return JsonResponse(
                    {'error': 'You are not participating in this game.'},
                    status=400
                )
            json_response = dict(
                success=True,
            )
            # don't return game info to leaving user - only success status
            return JsonResponse(json_response, status=200)
        else:  # game already started
            return JsonResponse(
                {
                    'error':
                        'This operation cannot be performed \
                        while game is active.'
                },
                status=400
            )
    # surrender running game
    elif action == 'surrender':
        # check if owner leaves the game
        if game.player_p1.user == request.user:
            game.game_end_status = 's'
            game.end()
            game.player_p2.won = True
            game.player_p2.save()
            return JsonResponse({'success': True}, status=200)
        # check if guest leaves the game
        elif game.player_p2.user == request.user:
            game.game_end_status = 's'
            game.end()
            game.player_p1.won = True
            game.player_p1.save()
            return JsonResponse({'success': True}, status=200)
        else:  # request user isn't participating in the game
            return JsonResponse(
                {'error': 'You are not participating in this game.'},
                status=400
            )


# get moves of given game (on GET)
# or make move (on POST)
@require_http_methods(["GET", "POST"])
def get_moves_or_make_move(request, id):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return JsonResponse({'error': "Given game doesn't exist"}, status=404)
    if request.method == "GET":
        # make list of all moves' jsons in given game
        game_moves = [move.as_json() for move in Move.get_game_moves(game)]
        return JsonResponse(game_moves, status=200, safe=False)
    elif request.method == "POST":
        my_player = game.get_my_player(request.user)
        # check if request user is participating in given game
        if my_player is None:
            return JsonResponse(
                {'error': 'You are not participating in this game.'},
                status=400
            )
        else:  # user is participating in this game
            x_coord = int(request.POST['x'])
            y_coord = int(request.POST['y'])
            my_move = Move(
                game=game,
                player=my_player,
                x_coordinate=x_coord,
                y_coordinate=y_coord,
            )
            move_status = game.make_move(my_move)
            # check if one of the players won or board is full (draw)
            game.check_game_end()
            # only successful move returns status 200
            if move_status['status'] == 200:
                json_response = dict(
                    game=game.as_json(),
                    move=my_move.as_json()
                )
                # return successful move's json
                return JsonResponse(json_response, status=200, safe=False)
            else:
                # get error message
                json_response = dict(
                    error=move_status['message']
                )
                # return incorrect move's json
                return JsonResponse(
                    json_response,
                    status=move_status['status'],
                    safe=False
                )


# return last move in given game
@require_http_methods(["GET"])
def get_last_move(request, id):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return JsonResponse({'error': "Given game doesn't exist"}, status=404)
    else:
        last_move = Move.get_game_moves(game).first()
    return JsonResponse(last_move.as_json(), status=200)
