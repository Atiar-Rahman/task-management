from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def Home(request):
    return HttpResponse('hekko')

def showTask(request):
    return HttpResponse('show all task')

def showSpecific_task(request,id):
    return HttpResponse(f"this is specific task page: {id}")