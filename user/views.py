from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, logout, login
from games.models import Game
from games.serializers import GameFullSerializer
from user.models import UserProfile
from user.serializers import UserProfileSerializer


# register new user
@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    username = request.POST['username']
    password = request.POST['password']
    # check if user of given username exists
    if UserProfile.is_username_taken(username=username):
        return Response(
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
    return Response(user_stats, status=201)


# log user in
@api_view(['POST'])
@permission_classes((AllowAny, ))
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:  # authentication success
        login(request, user)
        user_profile = UserProfile.objects.filter(username=username).first()
        user_stats = Game.get_user_stats(user=user_profile)
        return Response(user_stats, status=200)
    else:  # authentication failed
        return Response({'error': 'Authentication failed.'}, status=400)


# log user out
@api_view(['POST'])
def logout_user(request):
    if request.user.is_authenticated():
        logout(request)
        return Response(status=200)
    else:  # user isn't authenticated
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=403
        )


# get info about logged in user
@api_view(['GET', 'PATCH'])
def get_about_me(request):
    if request.user.is_authenticated():
        # PATCH = update username
        if request.method == "PATCH":
            serializer = UserProfileSerializer(
                request.user,
                request.data,
                partial=True,
            )
            if serializer.is_valid():
                serializer.save()
        # generate user's data (username + stats)
        user_stats = Game.get_user_stats(request.user)
        return Response(user_stats, status=200)
    else:
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=403
        )


# get info about some user
@api_view(['GET'])
def get_info(request, id):
    user = UserProfile.objects.filter(id=id).first()
    if user is not None:  # user of given id exists
        user_stats = Game.get_user_stats(user)
        return Response(user_stats, status=200)
    else:  # user of given id doesn't exist
        return Response(
            {'error': "User of given id doesn't exist."},
            status=404
        )


# get all active or awaiting games
@api_view(['GET'])
def get_active_awaiting_games(request):
    active_games = Game.get_user_awaiting_games(request.user)
    serializer = GameFullSerializer(active_games, many=True)
    return Response(serializer.data, status=200)


# get all finished games
@api_view(['GET'])
def get_finished_games(request):
    finished_games = Game.get_user_finished_games(request.user)
    serializer = GameFullSerializer(finished_games, many=True)
    return Response(serializer.data, status=200)
