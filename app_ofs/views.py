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


def get_categories_list (request) :
    with connection.cursor() as cursor:
        cursor.execute("SELECT category FROM category_info")
        categories_list = cursor.fetchall()

    return render(request, 'products.html', {'categories_list': categories_list})


def addProduct(request):
    if request.method == 'POST':
        product_id = random.randint(10000, 20000)
        product_name = request.POST['product_name']
        product_description = request.POST['product_description']


        if product_name:
            checkExistingProduct = "SELECT product_id FROM product_info WHERE product_name = %s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingProduct, (product_name,))
                getExistingProductData = cursor.fetchone()
        
            if getExistingProductData:
                return HttpResponse("Product already exists")


            sql_query = "INSERT INTO product_info (product_id, product_name, product_description) VALUES (%s, %s, %s)"
            values = (product_id, product_name, product_description)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, values)
                    connection.commit()

                return HttpResponseRedirect('/products')
            except IntegrityError:
                return HttpResponse("An error occurred while adding the product")
            
        else:
            return HttpResponse("Invalid product data")
    return render(request, 'products.html')


def getProduct(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM product_info")
        data = cursor.fetchall()

    products = []
    for row in data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
           
        }
        products.append(product)

    context = {
        'products': products,
    }

    return render(request, 'products.html', context)

def update_product(request):
    update_query = """
    UPDATE product_info
    SET product_name = %s, product_description = %s
    WHERE product_id = %s
    """
    
    if request.method == 'POST':
        product_id = request.POST['product_id']
        product_name = request.POST['product_name']
        product_description = request.POST['product_description']

        if product_id and product_name:
            with connection.cursor() as cursor:
                cursor.execute(update_query, (product_name, product_description, product_id))
                connection.commit()
            return HttpResponseRedirect('/products')
        else:
            return HttpResponse("Invalid product data")

    return render(request, 'products/.html')


# def delete_product(request, product_id):
#     if request.method == 'POST':
      
#         check_product_exists = "SELECT product_id FROM product_info WHERE product_id = %s"
#         with connection.cursor() as cursor:
#             cursor.execute(check_product_exists, (product_id,))
#             existing_product = cursor.fetchone()

#         if not existing_product:
#             return HttpResponse("Product not found")

#         # Delete the product
#         delete_query = "DELETE FROM product_info WHERE product_id = %s"
#         with connection.cursor() as cursor:
#             cursor.execute(delete_query, (product_id,))
#             connection.commit()

#         return HttpResponseRedirect('/products')
    
#     return render(request, 'products.html', {'product_id': product_id})

def delete_product(request, product_id):
    if request.method == 'POST':
        check_product_exists = "SELECT product_id FROM product_info WHERE product_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(check_product_exists, (product_id,))
            existing_product = cursor.fetchone()

        if not existing_product:
            return HttpResponse("failure")

        # Delete the product
        delete_query = "DELETE FROM product_info WHERE product_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(delete_query, (product_id,))
            connection.commit()

        return HttpResponse("success")

    return HttpResponse("Method not allowed")

def addOrder(request):
    if request.method == 'POST':
        order_id = random.randint(1000, 2000)
        order_product_name = request.POST['order_product_name']
        quantity = request.POST['quantity']
        ordered_date = request.POST['ordered_date']
        price = request.POST['price']
        delivery_date = request.POST['delivery_date']
        status = request.POST['status']

        sql_query = "INSERT INTO order_info (order_id, order_product_name, quantity,ordered_date , price, delivery_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (order_id, order_product_name, quantity,ordered_date , price, delivery_date, status)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/orders')
        except IntegrityError:
            return HttpResponse("An error occurred while adding the product")
            
       
    return render(request, 'orders.html')