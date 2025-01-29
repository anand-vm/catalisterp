#catalisterp/app/api/views.py
from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

def index(request):
    return JsonResponse({"message": "CatalistERP API V1.0!"})