from django.shortcuts import render
from ..models import Datasheet

def home(request):
    datasheets = Datasheet.objects.all()

    return render(request, 'home.html', {'datasheets': datasheets})