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
    

@api_view(['GET'])
def list_all_cases(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    cases = Case.objects.all()
    json_return = []
    for case in cases:
        json_return.append({
            'id': case.id,
            'title': case.title,
            'description': case.description,
            'created_at': case.created_at,
        })
    return Response({'status': 'success', 'message': 'Cases listed successfully', 'data': json_return})


@api_view(['GET'])
def list_all_truth_bullets(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    truth_bullets = TruthBullet.objects.all()
    json_return = []
    for truth_bullet in truth_bullets:
        json_return.append({
            'id': truth_bullet.id,
            'case_id': truth_bullet.case.id,
            'code': truth_bullet.code,
            'content': truth_bullet.content,
        })
    return Response({'status': 'success', 'message': 'Truth bullets listed successfully', 'data': json_return})


@api_view(['GET'])
def list_all_truth_bullets_by_case(request, case_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token or not case_id:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    case = get_object_or_404(Case, id=case_id)
    truth_bullets = TruthBullet.objects.filter(case=case)
    json_return = []
    for truth_bullet in truth_bullets:
        json_return.append({
            'id': truth_bullet.id,
            'case_id': truth_bullet.case.id,
            'name': truth_bullet.name, # 'Truth Bullet
            'code': truth_bullet.code,
            'content': truth_bullet.content,
        })
    return Response({'status': 'success', 'message': 'Truth bullets listed successfully', 'data': json_return})


@api_view(['GET'])
def get_truth_bullets_founded_by_user(request, case_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    case = get_object_or_404(Case, id=case_id)
    truth_bullets = TruthBullet.objects.filter(case=case, found_by=profile)
    json_return = []
    for truth_bullet in truth_bullets:
        json_return.append({
            'id': truth_bullet.id,
            'name': truth_bullet.name,
            'code': truth_bullet.code,
            'content': truth_bullet.content,
        })
    return Response({'status': 'success', 'message': 'Truth bullets listed successfully', 'data': json_return})


@api_view(['GET'])
def get_case(request, case_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    case = get_object_or_404(Case, id=case_id)
    json_return = {
        'id': case.id,
        'title': case.title,
        'description': case.description,
        'created_at': case.created_at,
    }
    return Response({'status': 'success', 'message': 'Case listed successfully', 'data': json_return})

@api_view(['GET'])
def get_truth_bullet(request, bullet_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    
    token = request.query_params.get('token')
    if not token:
        return Response({'status': 'error', 'message': 'Please enter all fields'})
    autentication_token = AuthToken.objects.filter(token=token).first()
    if autentication_token is None:
        return Response({'status': 'error', 'message': 'Invalid token'})
    
    profile = autentication_token.user
    truth_bullet = get_object_or_404(TruthBullet, id=bullet_id)
    json_return = {
        'id': truth_bullet.id,
        'case_id': truth_bullet.case.id,
        'code': truth_bullet.code,
        'content': truth_bullet.content,
    }
    return Response({'status': 'success', 'message': 'Truth bullet listed successfully', 'data': json_return})

@api_view(['POST'])
def add_truth_bullet_to_profile(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        bullet_code = request.data.get('bullet_code')
        case_id = request.data.get('case_id')
        if not token or not bullet_code or not case_id:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        if not TruthBullet.objects.filter(code=bullet_code, case_id=case_id).exists():
            return Response({'status': 'error', 'message': 'Invalid truth bullet code or case'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        if TruthBullet.objects.filter(code=bullet_code, case_id=case_id, found_by=profile).exists():
            return Response({'status': 'error', 'message': 'Truth bullet already added to profile'})
        truth_bullet = TruthBullet.objects.get(code=bullet_code, case_id=case_id)
        truth_bullet.found_by.add(profile)
        truth_bullet.save()
        return Response({'status': 'success', 'message': 'Truth bullet added to profile successfully'})
    

# Admin routes
@api_view(['POST'])
def create_case(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        title = request.data.get('title')
        description = request.data.get('description')
        if not token or not title or not description:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        case = Case.objects.create(
            user=profile, 
            title=title, 
            description=description, 
        )
        return Response({'status': 'success', 'message': 'Case created successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def create_truth_bullet(request):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        case_id = request.data.get('case_id')
        name = request.data.get('name') if request.data.get('name') else 'Truth Bullet'
        code = request.data.get('code') if request.data.get('code') else ''.join(random.choices(string.digits, k=8))
        content = request.data.get('content')
        if not token or not case_id or not code or not content:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        case = Case.objects.get(id=case_id)
        truth_bullet = TruthBullet.objects.create(
            case=case,
            name=name, 
            code=code,
            content=content
        )
        return Response({'status': 'success', 'message': 'Truth bullet created successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def delete_case(request, case_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        if not token:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        case = Case.objects.get(id=case_id)
        case.delete()
        return Response({'status': 'success', 'message': 'Case deleted successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def delete_truth_bullet(request, bullet_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        if not token:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        truth_bullet = TruthBullet.objects.get(id=bullet_id)
        truth_bullet.delete()
        return Response({'status': 'success', 'message': 'Truth bullet deleted successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def edit_case(request, case_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        title = request.data.get('title')
        description = request.data.get('description')
        if not token or not title or not description:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        case = Case.objects.get(id=case_id)
        case.title = title
        case.description = description
        case.save()
        return Response({'status': 'success', 'message': 'Case edited successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})

@api_view(['POST'])
def edit_truth_bullet(request, bullet_id):
    if not check_api_token(request):
        return Response({'status': 'error', 'message': 'Invalid API token'})
    if request.method == 'POST':
        token = request.data.get('token')
        code = request.data.get('code')
        content = request.data.get('content')
        if not token or not code or not content:
            return Response({'status': 'error', 'message': 'Please enter all fields'})
        autentication_token = AuthToken.objects.filter(token=token).first()
        if autentication_token is None:
            return Response({'status': 'error', 'message': 'Invalid token'})
        profile = autentication_token.user
        truth_bullet = TruthBullet.objects.get(id=bullet_id)
        truth_bullet.code = code
        truth_bullet.content = content
        truth_bullet.save()
        return Response({'status': 'success', 'message': 'Truth bullet edited successfully'})
    
    return Response({'status': 'error', 'message': 'Invalid request'})
