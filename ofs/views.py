from django.http import HttpResponse

from django.shortcuts import render

def loginPage(request):
    return render(request, "login.html")