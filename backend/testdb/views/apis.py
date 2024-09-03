from django.core.files.base import File
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.utils.timezone import make_aware
from django.core import serializers
import datetime
import os
import json
from ..models import Question, Answer, Conversation, Model, Datasheet, Component
from .utils import add_datasheet_from_upload, recommend_plot, get_answer, format_data, get_question_type

####################
# APIs             #
####################

@api_view(['POST'])
def upload_datasheet(request):
    if request.method == 'POST':
        datasheet_name = add_datasheet_from_upload(request)
        return Response({'datasheet': datasheet_name, 'uploaded':True}, content_type="application/json")

@api_view(['GET'])
def delete_datasheet(request):
    if request.method == 'GET':
        datasheet_name = request.GET.get('datasheet')
        datasheet = Datasheet.objects.get(datasheet_name=datasheet_name)
        datasheet.delete()

        return Response({'datasheet': datasheet_name, 'deleted':True}, content_type="application/json")

@api_view(['POST'])
def get_datasheets(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        user_email = json_request['user_email']
        if user_email == '':
            datasheets = Datasheet.objects.filter(user_email='-')
        else:
            datasheets = Datasheet.objects.filter(user_email=user_email)
        datasheets_ = serializers.serialize('json', datasheets)
        datasheets_json = json.loads(datasheets_)
        datasheets = []
        for datasheet in datasheets_json:
            datasheets.append(datasheet['fields'])
        return Response(datasheets)
    
@api_view(['POST'])
def classify_data(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        print(json_request)
        datasheet_name = json_request['datasheet_name']
        try:
            categorization = recommend_plot(datasheet_name)
        except:
            categorization = {"type": "none"}
        return Response(categorization, content_type="application/json")
    
@api_view(['POST'])
def assign_component_info(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        component_info = json_request['component_info']
        plot_type = json_request['plot_type']
        Component.objects.create(
            component_type=plot_type,
            component_info=component_info
        )
        return Response({"component_loaded": True}, content_type="application/json")
    
@api_view(['POST'])
def generate_data_format(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        data = format_data(json_request)
        return Response(data, content_type="application/json")

@api_view(['POST'])
def ask_question(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        question = json_request['question']
        conversation_id = json_request['conversation_id']
        model_name = json_request['model']
        datasheet_name = json_request['datasheet']
        new_conversation = json_request['new_conversation']

        timestamp = make_aware(datetime.datetime.now())
        model = Model.objects.get(model_name=model_name)
        datasheet = Datasheet.objects.get(datasheet_name=datasheet_name)

        question_type = get_question_type(question)['type']

        question_obj = Question.objects.create(
            question_text=question,
            question_type=question_type,
            model_type=model,
            saved_date_time=timestamp
        )

        if new_conversation:
            conversation = Conversation.objects.create(
                question_answer_count=1,
                conversation_datasheet=datasheet,
                start_date_time=timestamp
            )
        else:
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.question_answer_count += 1
            conversation.save()

        question_obj.conversation = conversation
        question_obj.save()

        answer, internal_json = get_answer(question, conversation, question_type)

        timestamp = make_aware(datetime.datetime.now())
        Answer.objects.create(
            answer_text = answer,
            model_type = model,
            answer_type = question_type,
            saved_date_time = timestamp,
            question = question_obj,
            # datasheet = datasheet,
            conversation = conversation
        )
        try:
            print("internal json: ", internal_json)
            internal_json = json.loads(internal_json)
        except:
            internal_json = []
        

        return Response({'answer': answer, 'conversation_id': conversation.id, 'internal_json': internal_json, 'type': question_type}, content_type="application/json")
    
@api_view(['POST'])
def get_component(request):
    if request.method == 'POST':
        return Response({'component': ""}, content_type="application/json")

@api_view(['GET'])
def get_conversations_by_datasheet(request):
    if request.method == 'GET':
        datasheet_name = request.GET.get('datasheet')
        datasheet = Datasheet.objects.get(datasheet_name=datasheet_name)
        conversations = Conversation.objects.filter(conversation_datasheet=datasheet)
        conversations_obj = []
        for conversation in conversations:
            conversation_id = conversation.pk
            questions = Question.objects.filter(conversation=conversation).order_by('saved_date_time')
            conversation_json = {}
            conversation_json['conversation_id'] = conversation_id
            conversation_json['questions_answers'] = []
            for question in questions:
                answers = Answer.objects.filter(question=question)
                qna_json = {
                    'question_id': question.pk,
                    'question': question.question,
                    'answers': [answer.answer_text for answer in answers]
                }
                conversation_json['questions_answers'].append(qna_json)
            conversations_obj.append(conversation_json)
        return Response({'conversations':conversations_obj})
    

@api_view(['POST'])
def add_ollama_models(request):
    if request.method == 'POST':
        json_request = JSONParser().parse(request)
        ollama_models = json_request['llms']
        for ollama_model in ollama_models:
            if Model.objects.filter(model_name=ollama_model['name']).count() == 0:
                Model.objects.create(
                    model_name=ollama_model['name'],
                    model_size=ollama_model['size']
                )
        return Response({'added':True}, content_type="application/json")