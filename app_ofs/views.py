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
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Pending'")
        pendingOrders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Ongoing'")
        ongoingOrders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Completed'")
        completedOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info")
        totalOrders = cursor.fetchone()[0]

        context = {
            'pendingOrder': pendingOrders,
            'ongoingOrder': ongoingOrders,
            'completedOrder': completedOrders,
            'totalOrder': totalOrders,
        }
    return render(request, 'dashboard/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')


def category(request):
    return render(request, 'category.html')

def products(request):
    return render(request, 'products.html')

def addnewproduct(request):
    return render (request, 'products/addnew-product.html')

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
        category = request.POST.get('category', None)

        if category is not None:
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
        old_category_id = request.POST.get('category_id', '')
        old_category_name = request.POST.get('old_category_name', '')

        sql_query = "UPDATE category_info SET category = %s WHERE category_id = %s"
        values = (old_category_name, old_category_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/category')
        except IntegrityError:
            return HttpResponse("An error occurred while editing the category name")
        
    return render(request, 'category.html')

def get_categories_list(request):
    categories_list = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, category FROM category_info")
        categories = cursor.fetchall()
        for category in categories:
            categories_list.append({'id': category[0], 'category': category[1]})

    return JsonResponse(categories_list, safe=False)

def addProduct(request):
    if request.method == 'POST':
        product_id = random.randint(10000, 20000)
        getCategory = request.POST.get('product_category')
        product_name = request.POST['product_name']
        product_description = request.POST['product_description']


        if product_name:
            checkExistingProduct = "SELECT product_id FROM product_info WHERE product_name = %s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingProduct, (product_name,))
                getExistingProductData = cursor.fetchone()
        
            if getExistingProductData:
                return HttpResponse("Product already exists")


            sql_query = "INSERT INTO product_info (product_id, category, product_name, product_description) VALUES (%s, %s, %s, %s)"
            values = (product_id, getCategory, product_name, product_description)

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
            'category': row[2],
            'product_name': row[3],
            'product_description': row[4],
        }
        products.append(product)

    context = {
        'products': products,
    }

    return render(request, 'products.html', context)


def editProduct(request):
    if request.method == 'POST':
        old_product_id = request.POST.get('product_id', '')
        new_product_name = request.POST.get('new_product_name', '')
        new_product_description = request.POST.get('new_product_description', '')

        sql_query = "UPDATE product_info SET product_name = %s, product_description = %s WHERE product_id = %s"
        values = (new_product_name, new_product_description, old_product_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/products')
        except IntegrityError:
            return HttpResponse("An error occurred while editing the product details")
        
    return render(request, 'products.html')

def delete_product(request, product_id):
    if request.method == 'POST':
        getProductID = request.POST.get('product_id', '')

        sql_query = "DELETE from product_info WHERE product_id = %s"
        values = (getProductID)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/products')
        except IntegrityError:
            return HttpResponse("An error occurred while deleting the products")
        
    return render(request, 'products.html')

def getOrder(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM order_info")
        data = cursor.fetchall()

    orders = []
    for row in data:
        order = {
            'order_id': row[1],
            'order_product_name': row[2],
            'quantity': row[3],
            'ordered_date': row[4],
            'price': row[5],
            'delivery_date': row[6],
            'status': row[7],
        }
        orders.append(order)

    context = {
        'orders': orders,
    }

    return render(request, 'orders.html', context)

def get_product_list(request):
    product_list = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, product_name FROM product_info")
        products = cursor.fetchall()
        for product in products:
            product_list.append({'id': product[0], 'product': product[1]})

    return JsonResponse(product_list, safe=False)

def addOrder(request):
    if request.method == 'POST':
        order_id = random.randint(1000, 2000)
        order_product_name = request.POST['order_product_name']
        quantity = request.POST['quantity']
        ordered_date = request.POST['ordered_date']
        price = request.POST['price']
        delivery_date = request.POST['delivery_date']
        status = request.POST['status']

        sql_query = "INSERT INTO order_info (order_id, order_product_name, quantity, ordered_date, price, delivery_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (order_id, order_product_name, quantity,ordered_date , price, delivery_date, status)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/orders')
        except IntegrityError:
            return HttpResponse("An error occurred while adding the product")
            
    return render(request, 'orders.html')

def delete_order(request, order_id):
    if request.method == 'POST':
        getOrderID = request.POST.get('order_id', '')
        sql_query = "DELETE from order_info WHERE order_id = %s"
        values = (getOrderID)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/orders')
        except IntegrityError:
            return HttpResponse("An error occurred while deleting the orders")
        
    return render(request, 'orders.html')

def getProductCategory(request):
    category = request.GET.get('category')
    print(category)

    product_list = []
    with connection.cursor() as cursor:
        sql_query = "SELECT id, product_name FROM product_info WHERE category = %s"
        cursor.execute(sql_query, [category])
        products = cursor.fetchall()
        print(products)
        for product in products:
            print(product[1])
            product_list.append({'id': product[0], 'product': product[1]})

    return JsonResponse(product_list, safe=False)

def addItems(request):
    if request.method == 'POST':
        productCategory = request.POST['product_category']
        product = request.POST['getProductCategory']
        quantity = request.POST['quantity']
        price = request.POST['price']


        sql_query = "INSERT INTO inventory_details (category, product, quantity, price) VALUES (%s, %s, %s, %s)"
        values = (productCategory, product, quantity, price)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/inventory')
        except IntegrityError:
            return HttpResponse("An error occurred while adding items into the inventory")

    return render(request, 'inventory.html')

def getItems(request):
    print("hello")
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM inventory_details")
        data = cursor.fetchall()

    itemList = []
    for row in data:
        items = {
            'category': row[1],
            'product': row[2],
            'quantity': row[3],
            'price': row[4],
        }
        itemList.append(items)

    context = {
        'items': itemList,
    }

    print(context)

    return render(request, 'inventory.html', context)