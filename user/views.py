from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, login
from django.http import JsonResponse
from games.models import Game
from user.models import UserProfile


# register new user
@require_http_methods(["POST"])
def register(request):
    username = request.POST['username']
    password = request.POST['password']
    # check if user of given username exists
    if UserProfile.is_username_taken(username=username):
        return JsonResponse(
            {'error': 'This username is already taken'},
            status=400
        )
    else:
        user = UserProfile.objects.create_user(
            username=username,
            password=password
        )
        # get stats of created user
        user_stats = Game.get_user_stats(user)
    return JsonResponse(user_stats, status=201, safe=False)


# log user in
@require_http_methods(["POST"])
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:  # authentication success
        login(request, user)
        user_profile = UserProfile.objects.filter(username=username).first()
        user_stats = Game.get_user_stats(user=user_profile)
        return JsonResponse(user_stats, status=200)
    else:  # authentication failed
        return JsonResponse({'error': 'Authentication failed.'}, status=400)


# log user out
@require_http_methods(["POST"])
def logout_user(request):
    if request.user.is_authenticated():
        logout(request)
        return JsonResponse({}, status=200)
    else:  # user isn't authenticated
        return JsonResponse(
            {'detail': 'Authentication credentials were not provided.'},
            status=403
        )


# get info about logged in user
@require_http_methods(["GET", "PATCH"])
def get_about_me(request):
    if request.user.is_authenticated():
        if request.method == "GET":
            # get stats of authenticated user
            user_stats = Game.get_user_stats(request.user)
            return JsonResponse(user_stats, status=200)
        elif request.method == "PATCH":
            # TODO
            return JsonResponse({'error': 'Not implemented yet'}, status=500)
    else:
        return JsonResponse(
            {'detail': 'Authentication credentials were not provided.'},
            status=403
        )


# get info about some user
@require_http_methods(["GET"])
def get_info(request, id):
    user = UserProfile.objects.filter(id=id).first()
    if user is not None:  # user of given id exists
        user_stats = Game.get_user_stats(user)
        return JsonResponse(user_stats, status=200)
    else:  # user of given id doesn't exist
        return JsonResponse(
            {'error': "User of given id doesn't exist."},
            status=404
        )


# get all active or awaiting games
@require_http_methods(["GET"])
def get_active_awaiting_games(request):
    active_games = Game.get_user_awaiting_games(request.user)
    json_response = [game.as_json() for game in active_games]
    return JsonResponse(json_response, status=200, safe=False)


# get all finished games
@require_http_methods(["GET"])
def get_finished_games(request):
    finished_games = Game.get_user_finished_games(request.user)
    json_response = [game.as_json() for game in finished_games]
    return JsonResponse(json_response, status=200, safe=False)
