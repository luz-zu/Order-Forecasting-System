from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseNotFound
from django.http import JsonResponse
from .forms import RegisterForm
from django.db import connection, IntegrityError
import random
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.template.loader import get_template



def index(request):
    return render(request, 'index.html')


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
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('login')
        else:   
            messages.error(request, 'Registration failed. Please check the provided information.')

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


def forgetpassword(request):
    return render(request, 'forgetpassword.html')


def send_otp(request):
    if request.method == 'POST':
        email = request.POST['email']
        with connection.cursor() as cursor:
            # Use raw SQL query to get the user based on email
            cursor.execute("SELECT * FROM app_ofs_customuser WHERE email = %s", [email])
            row = cursor.fetchone()

        if row:
            user_id = row[0]
            username = row[4]
            db_email = row[7]

            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')

            # Store OTP in the database
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE app_ofs_customuser SET otp = %s, otp_created_at = %s WHERE id = %s",
                    [otp, timezone.now(), user_id]
                )

            # Send OTP via Email
            subject = 'OFS Forget Password'
            
            message = f'Hello {username},<br><br>'
            message += 'You requested a password reset. Please use the following OTP to proceed:<br><br>'
            message += f'<strong>OTP: {otp}</strong><br><br>'
            message += 'This OTP is valid for 15 minutes.<br>'
            message += 'If you did not request a password reset, please ignore this email.<br><br>'
            message += 'Thank You!'

            from_email = 'Order Forecasting System'
            recipient_list = [db_email]

            send_mail(subject, message, from_email, recipient_list, html_message=message)

            return render(request, 'forgetpassword.html', {'otp_sent': True, 'email': db_email})
        else:
            return render(request, 'forgetpassword.html', {'user_not_found': True, 'error': 'Email not found!'})
    else:
        return render(request, 'forgetpassword.html', {'otp_sent': False, 'otp_verified': False})

def verify_otp(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            otp_entered = request.POST['otp']

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM app_ofs_customuser WHERE email = %s AND otp = %s AND otp_created_at >= %s",
                    [email, otp_entered, timezone.now() - timezone.timedelta(minutes=15)]
                )
                row = cursor.fetchone()

            if row:
                user_id = row[0]
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE app_ofs_customuser SET otp_verified = TRUE WHERE id = %s", [user_id])

                return render(request, 'forgetpassword.html', {'otp_verified': True, 'email': email})
            else:
                return render(request, 'forgetpassword.html', {'otp_verified': False, 'email': email})
        except MultiValueDictKeyError:
            return render(request, 'forgetpassword.html', {'otp_verified': False, 'email_not_found': True})
    else:
        return render(request, 'forgetpassword.html', {'otp_verified': False, 'otp_sent': False})

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if len(new_password) < 8:
            return render(request, 'forgetpassword.html', {'otp_verified': True, 'error': 'Password should be at least 8 characters long.'})


        if new_password == confirm_password:
            hashed_password = make_password(new_password)
            with connection.cursor() as cursor:
                cursor.execute("UPDATE app_ofs_customuser SET password = %s WHERE email = %s", [hashed_password, email])

            return render(request, 'login.html')
        else:
            error = "Passwords do not match."
            return render(request, 'forgetpassword.html', {'otp_verified': True, 'error': error, 'email': email})
    else:
        return render(request, 'login.html')
    


def editprofile(request):
    if request.method == 'POST':
        # Get the updated data from the form
        new_username = request.POST.get('edit_username')
        new_email = request.POST.get('edit_email')
        new_phonenumber = request.POST.get('edit_phonenumber')

        # Update user information
        user = request.user
        user.username = new_username
        user.email = new_email
        user.phonenumber = new_phonenumber
        user.save()

        # messages.success(request, 'Profile updated successfully!')

    return render(request, 'editprofile.html')

def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('edit_old_pass')
        new_password = request.POST.get('edit_new_pass')
        confirm_password = request.POST.get('edit_confirm_pass')

        user = request.user

        # Check if the old password matches the user's current password
        if user.check_password(old_password):
            # Check if the new password and confirm password match
            if new_password == confirm_password:
                # Set the new password for the user
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Password changed successfully!')
                return redirect('editprofile')  # Redirect to profile or any desired page after password change
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Invalid old password.')

    
    return render(request, 'changepassword.html')
