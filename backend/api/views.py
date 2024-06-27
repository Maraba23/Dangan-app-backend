import profile
from sys import api_version
import unicodedata
from rest_framework import generics, permissions
from rest_framework.response import Response
from usuarios.models import *
from .serializers import *
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from rest_framework.decorators import api_view
from usuarios.models import *
from django.shortcuts import render, redirect
import sweetify
import datetime
import requests
import logging
from django.utils.encoding import force_bytes, smart_str, smart_bytes, DjangoUnicodeDecodeError
import os
import zipfile
from django.utils import timezone
from django.http import HttpResponse, Http404, JsonResponse
import random
import string
from django.views.decorators.csrf import csrf_exempt
import math
from dotenv import load_dotenv
import json
import pandas as pd
from django.shortcuts import get_object_or_404
import logging
from django.utils.dateformat import format
import pytz
from datetime import timedelta

logger = logging.getLogger(__name__)

load_dotenv()

def check_api_token(request):
    api_token = request.headers.get('Authorization')
    if api_token != os.getenv('API_TOKEN'):
        return False
    return True

@api_view(['POST'])
def register(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = "user"
        if not username or not email or not password or not role:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': 'Username is already taken'})
        if User.objects.filter(email=email).exists():
            return Response({'status': 'error', 'message': 'Email is already taken'})
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(user=user, username=username, email=email, role=role)
        return Response({'status': 'success', 'message': 'User created successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def login(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'status': 'error', 'message': 'Invalid credentials'})
        if not user.check_password(password):
            return Response({'status': 'error', 'message': 'Invalid credentials'})
        profile = Profile.objects.get(user=user)
        autentication_token = AuthToken.objects.create(
            user=profile, 
            token=''.join(random.choices(string.ascii_letters + string.digits, k=200)),
            created_at=timezone.now()
        )
        return Response({'status': 'success', 'message': 'User logged in successfully', 'token': autentication_token.token})
    
    return Response({'status': 'error', 'message': 'Invalid request'})


@api_view(['POST'])
def token_checker(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    print(request.data)
    token = request.data.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token.created_at < timezone.now() - datetime.timedelta(days=1):
        autentication_token.delete()
        return Response({'status': 'error', 'message': 'Token expired'})
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    json_return = {}
    profile = autentication_token.user
    json_return['id'] = profile.id
    json_return['username'] = profile.username
    json_return['email'] = profile.email
    json_return['role'] = profile.role
    return Response({'status': 'success', 'message': 'Token is valid', 'data': json_return})
    
    return Response({'status': 'error', 'message': 'Invalid request'})