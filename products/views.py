from django.shortcuts import render
from .models import Productos

# Create your views here.

def home(request):
    return render(request, 'baseInterface.html',{'productos': Productos.objects.all()})
