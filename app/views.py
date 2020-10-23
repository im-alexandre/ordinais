from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    """docstring"""
    return HttpResponse("<H1> Testando!!!</H1>")
