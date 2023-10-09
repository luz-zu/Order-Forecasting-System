from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from .forms import RegisterForm
from django.db import connection, IntegrityError
import random

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
            return redirect('login')
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

def inventory(request):
    return render(request, 'inventory.html')


def getCategory(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM category_info")
        data = cursor.fetchall()

    categories = []
    for row in data:
        category = {
            'category_id': row[1],
            'category': row[2],
           
        }
        categories.append(category)

    context = {
        'categories': categories,
    }

    return render(request, 'category.html', context)

def addCategory(request):
    if request.method == 'POST':
        category_id = random.randint(1000, 9999)
        category = request.POST['category']

        if category:
            checkExistingCategory = "SELECT category_id FROM category_info WHERE category = %s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingCategory, (category,))
                getExistingCategoryData = cursor.fetchone()
        
            if getExistingCategoryData:
                return HttpResponse("Category already exists")


            sql_query = "INSERT INTO category_info (category_id, category) VALUES (%s, %s)"
            values = (category_id, category)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, values)
                    connection.commit()

                return HttpResponseRedirect('/category')
            except IntegrityError:
                return HttpResponse("An error occurred while adding the category")
            
        else:
            return HttpResponse("Invalid category data")
    return render(request, 'category.html')

def editCategory(request):
    if request.method == 'POST':
        old_category_name = request.POST['old_category']
        new_category_name = request.POST['new_category_name']

        if (old_category_name & new_category_name):
            
            return

    return
