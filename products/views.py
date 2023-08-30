from django.shortcuts import render, redirect
from .models import Productos
from django.http import HttpResponse
from django.urls import reverse



def Home(request):
    product = Productos.objects.all()
    return render(request, 'providersHome.html', {"Products":product})  # Enviar lista

