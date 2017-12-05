from rest_framework.decorators import api_view
from rest_framework.response import Response
import simplejson as json
from games.models import Game, Move, Player
from games.serializers import GameSerializer, GameFullSerializer
from games.serializers import MoveSerializer


# create new game with empty board on POST
# or return awaiting games on GET
@api_view(['GET', 'POST'])
def create_new_or_get_awaiting(request):
    if request.method == 'POST':
        new_game = Game.objects.create(
            board=json.dumps(Game.create_new_board()),
            players_count=1
        )
        my_player = Player.objects.create(
            user=request.user,
            game=new_game,
            owner=True,
            first=False
        )
        serializer = GameFullSerializer(new_game)
        return Response(serializer.data, status=201)
    else:
        # only authenticated user can get list of awaiting games
        if request.user.is_authenticated():
            serializer = GameSerializer(Game.get_awaiting_games(), many=True)
            return Response(serializer.data, status=200)
        else:  # unauthenticated user
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=403
            )


# return detailed info about given game
# @require_http_methods(["GET"])
@api_view(['GET'])
def get_detailed_info(request, id):
    game = Game.objects.filter(id=id).first()
    if game is not None:
        serializer = GameSerializer(game)
        return Response(serializer.data, status=200)
    else:
        return Response({'error': "Given game doesn't exist"}, status=404)


# perform given action (create/join/leave/surrender)
@api_view(['POST'])
def perform_action(request, id, action):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return Response({'error': "Given game doesn't exist"}, status=404)
    elif action == "join":  # join to awaiting game
        # check if there is empty seat in given game
        if game.get_number_of_players() == 1:
            if Player.objects.filter(user=request.user, game=game).exists():
                return Response(
                    {'error': 'You are already a player in this game.'},
                    status=400
                )
            else:
                my_player = Player.objects.create(
                    user=request.user,
                    first=False,
                    game=game,
                    owner=False
                )
                game.players_count += 1
                game.save()
                serializer = GameFullSerializer(game)
                json_response = dict(
                    game=serializer.data,
                    success=True,
                )
                return Response(json_response, status=200)
        else:  # game is full
            return Response(
                {'error': 'This game is already full.'},
                status=400
            )
    # start awaiting game
    elif action == "start":
        # check if there are 2 players in given game
        if game.get_number_of_players() == 2:
            my_player = Player.objects.filter(
                game=game,
                user=request.user
            ).first()
            if my_player is not None:
                my_player.first = True
                my_player.save()
            else:
                return Response(
                    {'error': 'You are not participating in this game.'},
                    status=400
                )
            game.start()
            serializer = GameFullSerializer(game)
            json_response = dict(
                game=serializer.data,
                success=True,
            )
            return Response(json_response, status=200)
    # leave given game
    elif action == 'leave':
        # check if given game already started
        if not game.is_started():
            leaving_player = Player.objects.filter(
                game=game,
                user=request.user
            ).first()
            if leaving_player is not None:
                # check if there are 2 players in the game
                if game.get_number_of_players() == 2:
                    staying_player = Player.objects\
                        .filter(game=game)\
                        .exclude(user=request.user).first()
                    # guest is new owner
                    staying_player.owner = True
                    staying_player.save()
                    leaving_player.delete()
                    game.players_count -= 1
                    game.save()
                else:  # there is no guest in the game
                    leaving_player.delete()
                    game.delete()
            else:
                return Response(
                    {'error': 'You are not participating in this game.'},
                    status=400
                )
            json_response = dict(
                success=True,
            )
            # don't return game info to leaving user - only success status
            return Response(json_response, status=200)
        else:  # game already started
            return Response(
                {
                    'error':
                        'This operation cannot be performed '
                        'while game is active.'
                },
                status=400
            )
    # surrender running game
    elif action == 'surrender':
        # check if owner leaves the game
        surrender_player = Player.objects.filter(
            game=game,
            user=request.user
        ).first()
        if surrender_player is not None:
            game.game_end_status = 's'
            game.end()
            winner_player = Player.objects\
                .filter(game=game)\
                .exclude(user=request.user).first()
            winner_player.won = True
            winner_player.save()
            return Response({'success': True}, status=200)
        else:  # request user isn't participating in the game
            return Response(
                {'error': 'You are not participating in this game.'},
                status=400
            )


# get moves of given game (on GET)
# or make move (on POST)
@api_view(['GET', 'POST'])
def get_moves_or_make_move(request, id):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return Response({'error': "Given game doesn't exist"}, status=404)
    if request.method == "GET":
        # make list of all moves' jsons in given game
        serializer = MoveSerializer(Move.get_game_moves(game), many=True)
        return Response(serializer.data, status=200)
    elif request.method == "POST":
        my_player = Player.objects.filter(game=game, user=request.user).first()
        # check if request user is participating in given game
        if my_player is None:
            return Response(
                {'error': 'You are not participating in this game.'},
                status=400
            )
        else:  # user is participating in this game
            x_coord = int(request.POST['x'])
            y_coord = int(request.POST['y'])
            my_move = Move(
                game=game,
                player=my_player,
                x=x_coord,
                y=y_coord,
            )
            move_status = game.make_move(my_move)
            # check if one of the players won or board is full (draw)
            game.check_game_end()
            # only successful move returns status 200
            if move_status['status'] == 200:
                game_serializer = GameFullSerializer(game)
                # mo
                json_response = dict(
                    game=game_serializer.data,
                    move=my_move.as_json()
                )
                # return successful move's json
                return Response(json_response, status=200)
            else:
                # get error message
                json_response = dict(
                    error=move_status['message']
                )
                # return incorrect move's json
                return Response(
                    json_response,
                    status=move_status['status'],
                )


# return last move in given game
@api_view(['GET'])
def get_last_move(request, id):
    game = Game.objects.filter(id=id).first()
    if game is None:
        return Response({'error': "Given game doesn't exist"}, status=404)
    else:
        last_move = Move.get_game_moves(game).first()
        serializer = MoveSerializer(last_move)
    return Response(serializer.data, status=200)
