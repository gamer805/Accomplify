from django.core.files.base import File
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.utils.timezone import make_aware
from django.core import serializers
import datetime
import os
import json
from ..models import List, Task, Attachment
from .utils import update_tasklist


@api_view(['POST'])
def save_tasklist(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        list_name = json_request['name']
        list_category = json_request['category']
        tasks = json_request['tasks']
        print("Tasks: ", tasks)
        
        labels = []
        dates = []
        task_ids = []
        
        for task in tasks:
            labels.append(task['label'])
            dates.append(task['date'])
            task_ids.append(task['id'])
        
        task = update_tasklist(list_name, list_category, labels, dates, task_ids)
        return Response({"task updated": True}, content_type="application/json")