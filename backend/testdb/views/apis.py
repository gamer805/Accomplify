from django.core.files.base import File
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.utils.timezone import make_aware
from django.core import serializers
from google.oauth2 import id_token
from google.auth.transport import requests

from ..models import List, Task, Attachment, AccomplifyUser
from .utils import update_tasklist, collect_tasklist
import datetime
import os
import json


@api_view(['POST'])
def save_tasklist(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        print("TaskList: ", json_request)
        list_name = json_request['name']
        list_category = json_request['category']
        tasks = json_request['tasks']
        user_email = json_request['email'] or ''
        
        user = AccomplifyUser.objects.get(email=user_email)
        print("Tasks: ", tasks)
        
        labels = []
        dates = []
        task_ids = []
        
        for task in tasks:
            labels.append(task['label'])
            dates.append(task['date'])
            task_ids.append(task['id'])
        
        task = update_tasklist(list_name, list_category, user, labels, dates, task_ids)
        return Response({"task updated": True}, content_type="application/json")

@api_view(['POST'])
def get_tasklist(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        user_email = json_request['user_email']
        user = AccomplifyUser.objects.get(email=user_email)
        task_collection = collect_tasklist(user)
        return Response({"task_collection": task_collection}, content_type="application/json")

@api_view(['POST'])
def google_login(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        token = json_request['token']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.environ['GOOGLE_CLIENT_ID'])
            
            print(f"Received token: {token}")
            print(f"Decoded token info: {idinfo}")
            
            print(idinfo)
            email = idinfo['email']
            name = idinfo['name']
            given_name = idinfo['given_name']
            picture = idinfo['picture']
            
            user, created = AccomplifyUser.objects.get_or_create(email=email, defaults = {name: name, given_name: given_name, picture: picture})
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'picture': user.picture
                }
            })
        except ValueError as e:
            print(f"Error verifying Google token: {str(e)}")
            return Response({'error': str(e)}, status=400, content_type="application/json")
        except Exception as e:
            print(f"Unexpected error in Google login: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=500, content_type="application/json")