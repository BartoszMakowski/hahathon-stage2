from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, login
from rest_framework import status
from rest_framework.response import Response

from django.http import JsonResponse
from django.core import serializers

from games.models import Game
from user.models import UserProfile
from django.contrib.auth.models import User


@require_http_methods(["POST"])
def register(request):
    username = request.POST['username']
    password = request.POST['password']
    if UserProfile.is_username_taken(username=username):
        return JsonResponse({'error': 'This username is already taken'}, status=400)
    else:
        data = dict(
            username=username,
            password=password
        )
        user = UserProfile.objects.create_user(username=username, password=password)
        user_stats = Game.get_user_stats(user)
    return JsonResponse(user_stats, status=201, safe=False)


@require_http_methods(["POST"])
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        user_profile = UserProfile.objects.filter(username=username).first()
        if user_profile is not None:
            user_stats = Game.get_user_stats(user=user_profile)
            return JsonResponse(user_stats, status=200)
        return JsonResponse({}, status=400)
        # user_serializer = UserProfileSerializer(user_profile, context=serializer_context)

    else:
        return JsonResponse({}, status=400)


@require_http_methods(["POST"])
def logout_user(request):
    if request.user is not None:
        logout(request)
        return JsonResponse({}, status=200)
    else:
        return JsonResponse({}, status=403)


@require_http_methods(["GET", "PATCH"])
def get_about_me(request):
    if request.user.is_authenticated():
        if request.method == "GET":
            user_stats = Game.get_user_stats(request.user)
            return JsonResponse(user_stats, status=200)

        elif request.method == "PATCH":
            user_info = {}
            return user_info
    else:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=403)


@require_http_methods(["GET"])
def get_info(request, id):
    try:
        user = UserProfile.objects.get(id=id)
        user_stats = Game.get_user_stats(user)
        return JsonResponse(user_stats, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({}, status=404)


@require_http_methods(["GET"])
def get_active_awaiting_games(request):
    active_games = Game.get_user_awaiting_games(request.user)
    json_response = [game.as_json() for game in active_games]
    return JsonResponse(json_response, status=200, safe=False)


@require_http_methods(["GET"])
def get_finished_games(request):
    finished_games = Game.get_user_finished_games(request.user)
    json_response = [game.as_json() for game in finished_games]
    return JsonResponse(json_response, status=200, safe=False)
