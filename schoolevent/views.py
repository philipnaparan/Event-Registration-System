from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime



def home(request):
    context = dict()
    context['page_title'] = 'Event Registration System'
    context['data'] = datetime.now()
    return render(request, 'index.html', context)