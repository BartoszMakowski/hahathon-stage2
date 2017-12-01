from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, login
from rest_framework import status
from rest_framework.response import Response

from django.http import JsonResponse
from django.core import serializers

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
    return JsonResponse(user.as_json() , status=201, safe=False)


@require_http_methods(["POST"])
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        try:
            user_profile = UserProfile.objects.get(username=username)
        except:
            return JsonResponse({}, status=400)
        # user_serializer = UserProfileSerializer(user_profile, context=serializer_context)
        return JsonResponse(user_profile.as_json(), status=200)
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
    if request.method == "GET":
        try:
            user_profile = UserProfile.objects.get(username=request.user.username)
            return JsonResponse(user_profile.as_json(), status=200)
        except:
            return JsonResponse({}, status=400)

    elif request.method == "PATCH":
        user_info = {}
        return user_info

@require_http_methods(["GET"])
def get_info(request, id):
    try:
        user_profile = UserProfile.objects.get(id=id)
        return JsonResponse(user_profile.as_json(), status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({}, status=404)



@require_http_methods(["GET"])
def get_active_awaiting_games(request):
    active_games = []
    return active_games

@require_http_methods(["GET"])
def get_finished_games(request):
    finished_games = []
    return finished_games

