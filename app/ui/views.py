#catalisterp/app/ui/views.py
from django.shortcuts import render


# Render App Landing Page
def index(request):
    return render(request, 'core/index.html')