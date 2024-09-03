from django.core.files.base import File
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.utils.timezone import make_aware
from django.core import serializers
import datetime
import os
import json
from ..models import Category, List, Task, Attachment
from .utils import update_task


@api_view(['POST'])
def save_task(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        name = json_request['name']
        tasks = json_request['tasks']
        date = json_request['date']
        task = update_task(name, tasks, date)
        return Response(task, content_type="application/json")