from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .forms import RegisterForm
from django.db import connection

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        user_ip_address = request.META.get('REMOTE_ADDR')
        if user is not None:
            login(request, user)
            description = "logged in"
            sql_query = "INSERT INTO logs (username, ip, description) VALUES (%s, %s, %s)"
            values = (username, user_ip_address, description)

            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            return HttpResponseRedirect('/dashboard')
        else:
            description = "Incorrect username/password"
            sql_query = "INSERT INTO logs (username, ip, description) VALUES (%s, %s, %s)"
            values = (username, user_ip_address, description)

            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            return render(request, 'login.html', {'error': 'Invalid Username or Password'})
    return render(request, 'login.html')

def register(request): 
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Redirect to your homepage or a success page
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def category(request):
    return render(request, 'category.html')

def products(request):
    return render(request, 'products.html')

def addnewproduct(request):
    return render (request, 'products/addnew-product.html')

def orders(request):
    return render(request, 'orders.html')