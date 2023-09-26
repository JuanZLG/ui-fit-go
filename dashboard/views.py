from django.shortcuts import render

# Create your views here.

def Entrance(request):
    return render(request, 'tgoEntrance.html')

def Home(request):
    return render(request, 'dashboard.html')