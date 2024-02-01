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
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.views.decorators.cache import never_cache
from datetime import datetime, timedelta

from django.db.models import Sum

# views.py
from django.shortcuts import render
from .models import SalesData
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
import statsmodels.api as sm
import pmdarima as pm
from io import BytesIO
import base64
import plotly.graph_objects as go

import plotly.express as px
from plotly.offline import plot
# My Algorithm
import pandas as pd
import numpy as np
from django.shortcuts import render
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import statsmodels.api as sm
import pmdarima as pm
from statsmodels.tsa.stattools import adfuller, acf, pacf

def get_image():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


def previous_pg(request):
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)

def not_logged_in(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            # Redirect authenticated users to a specific URL, like the dashboard
            return redirect('/dashboard')
    return wrap

@not_logged_in
@never_cache
def index(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'aboutus.html')

@not_logged_in
@never_cache
def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        user_ip_address = request.META.get('REMOTE_ADDR')
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! You have successfully logged in.')
            description = "logged in"
            sql_query = "INSERT INTO logs (username, ip, description) VALUES (%s, %s, %s)"
            values = (username, user_ip_address, description)
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            return redirect('/dashboard')
        else:
            description = "Incorrect username/password"
            sql_query = "INSERT INTO logs (username, ip, description) VALUES (%s, %s, %s)"
            values = (username, user_ip_address, description)
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            messages.error(request,'Invalid Username or Password')
            return render(request, 'login.html')
    return render(request, 'login.html')


@not_logged_in
@never_cache

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM app_ofs_customuser WHERE email = %s", [email])
                count = cursor.fetchone()[0]

            if count > 0:
                messages.error(request, 'Email already exists. Please use a different email address.')
            else:
                # Generate a random 2-digit company_id
                form.instance.userrole = 'admin'
                form.instance.company_id = 1
                form.save()
                messages.success(request, 'Registration successful! You are now logged in.')
                return HttpResponseRedirect('/register')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def forecast(request):
    current_user_id = request.user.added_by

    query = "SELECT ordered_date, quantity FROM forecast_data"

    with connection.cursor() as cursor:
        cursor.execute(query)
        forecast_data = cursor.fetchall()

    forecast_df = pd.DataFrame(forecast_data, columns=['ordered_date', 'quantity'])

    try:
        results = arima_sarimax_forecast(forecast_df)
    except Exception as e:
        results = {'sarimax_forecast': [], 'sarimax_confidence_intervals': {'lower quantity': [], 'upper quantity': []}}

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Pending' AND userid = %s", (current_user_id,))
        pendingOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Ongoing' AND userid = %s", (current_user_id,))
        ongoingOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Completed' AND userid = %s", (current_user_id,))
        completedOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE userid = %s", (current_user_id,))
        totalOrders = cursor.fetchone()[0]

    sarimax_chart = go.Figure()

    sarimax_chart.add_trace(go.Scatter(x=forecast_df['ordered_date'], y=forecast_df['quantity'], mode='lines', name='Actual Quantity'))

    last_date = forecast_df['ordered_date'].max()
    sarimax_forecast_index = pd.date_range(start=last_date, periods=13, freq='M')[1:]
    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index, y=results['sarimax_forecast'], mode='lines', name='SARIMAX Forecast'))

    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index,
                                       y=results['sarimax_confidence_intervals']['lower quantity'],
                                       fill=None,
                                       mode='lines',
                                       line=dict(color='rgba(100, 100, 255, 0.3)'),
                                       name='SARIMAX Lower CI'))

    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index,
                                       y=results['sarimax_confidence_intervals']['upper quantity'],
                                       fill='tonexty',
                                       mode='lines',
                                       line=dict(color='rgba(100, 100, 255, 0.3)'),
                                       name='SARIMAX Upper CI'))

    sarimax_chart.update_layout(title='SARIMAX Forecast with Confidence Intervals')

    sarimax_chart_html = sarimax_chart.to_html(full_html=False)

    context = {
        'pendingOrder': pendingOrders,
        'ongoingOrder': ongoingOrders,
        'completedOrder': completedOrders,
        'totalOrder': totalOrders,
        'results': results,
        'sarimax_chart_html': sarimax_chart_html,
    }

    return render(request, 'forecast.html', context)

@login_required
def user_dashboard(request):
    current_user_id = request.user.added_by

    data = pd.read_csv("/home/lujana/Order-Forecasting-System/app_ofs/data/Electric_Production.csv")
    data.columns = ["Month", "Sales"]
    data = data.dropna()

    results = arima_sarimax_forecast(data)

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Pending' AND userid = %s", (current_user_id,))
        pendingOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Ongoing' AND userid = %s", (current_user_id,))
        ongoingOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE status = 'Completed' AND userid = %s", (current_user_id,))
        completedOrders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_info WHERE userid = %s", (current_user_id,))
        totalOrders = cursor.fetchone()[0]

    sarimax_chart = go.Figure()

    # Plot actual data
    sarimax_chart.add_trace(go.Scatter(x=data.index, y=data['Sales'], mode='lines', name='Actual Sales'))

    # Plot SARIMAX Forecast
    last_date = data.index[-1]
    sarimax_forecast_index = pd.date_range(start=last_date, periods=13, freq='M')[1:]
    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index, y=results['sarimax_forecast'], mode='lines', name='SARIMAX Forecast'))

    # Plot confidence intervals
    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index,
                                       y=results['sarimax_confidence_intervals']['lower Sales'],
                                       fill=None,
                                       mode='lines',
                                       line=dict(color='rgba(100, 100, 255, 0.3)'),
                                       name='SARIMAX Lower CI'))

    sarimax_chart.add_trace(go.Scatter(x=sarimax_forecast_index,
                                       y=results['sarimax_confidence_intervals']['upper Sales'],
                                       fill='tonexty',
                                       mode='lines',
                                       line=dict(color='rgba(100, 100, 255, 0.3)'),
                                       name='SARIMAX Upper CI'))

    sarimax_chart.update_layout(title='SARIMAX Forecast with Confidence Intervals')

    # Convert SARIMAX chart to HTML
    sarimax_chart_html = sarimax_chart.to_html(full_html=False)

    context = {
        'pendingOrder': pendingOrders,
        'ongoingOrder': ongoingOrders,
        'completedOrder': completedOrders,
        'totalOrder': totalOrders,
        'results': results,
        'sarimax_chart_html': sarimax_chart_html,
    }

    return render(request, 'dashboard/dashboard.html', context)




# @login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')

@login_required
def category(request):
    return render(request, 'category.html')

@login_required
def products(request):
    
    return render(request, 'products.html')

@login_required
def addnewproduct(request):
    return render (request, 'products/addnew-product.html')


@login_required

def inventory(request):
    current_user_id = request.user.added_by
  
    sql_category_with_count = """
        SELECT
            c.category_id,
            c.category,
            COUNT(p.product_id) AS total_products
        FROM
            category_info c
        LEFT JOIN
            product_info p ON c.category_id = p.category
        WHERE
            c.userid = %s
        GROUP BY
            c.category_id, c.category
    """

    value = (current_user_id,)
    with connection.cursor() as cursor:
        cursor.execute(sql_category_with_count, value)
        categories_with_count = cursor.fetchall()

    categories = []
    for row in categories_with_count:
        category_id = row[0]
        category_name = row[1]
        total_products = row[2]

        # Only include categories with a count greater than 0
        if total_products > 0:
            category = {
                'category_id': category_id,
                'category': category_name,
                'total_products': total_products,
            }
            categories.append(category)

    context = {
        'categories': categories,
    }

    return render(request, 'inventory.html', context)

@login_required
def staff(request):
    current_user_id = request.user.added_by
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM app_ofs_customuser WHERE userrole = 'staff' AND added_by = %s", [current_user_id])
        staff_members = cursor.fetchall()
    
    staff_details = []
    for row in staff_members:
        staff = {
            'fname': row[6],
            'lname': row[7],
            'username': row[5],
            'email': row[8],
            'phone': row[13],
            'role': row[17],
        }
        staff_details.append(staff)
    
    context = {
        'staff_members': staff_details
    }
    return render(request, 'staff.html', context)

@login_required


def addStaff(request):
    if request.method == 'POST':
        # Get current user ID
        current_user_id = request.user.id if request.user.is_authenticated else None

        fname = request.POST.get('first_name', '')
        lname = request.POST.get('last_name', '')
        email = request.POST.get('staff_email', '')
        password = 'ofs@12345'  # Note: You may want to generate a secure password
        phone = request.POST.get('staff_phone', '')
        role = request.POST.get('staff_role', '')

        # Validate phone number length
        if len(phone) != 10:
            messages.error(request, 'Phone number must be 10 digits.')
            return HttpResponseRedirect('/staff')

        # Check if the email already exists
        email_exists_query = "SELECT COUNT(*) FROM app_ofs_customuser WHERE email = %s"
        email_exists_values = (email,)

        with connection.cursor() as cursor:
            cursor.execute(email_exists_query, email_exists_values)
            email_count = cursor.fetchone()[0]

        if email_count > 0:
            messages.error(request, 'Email already exists. Please use a different email address.')
            return HttpResponseRedirect('/staff')

        # Generate a random username
        randNumber = random.randint(100, 999)
        username = f'{fname.lower()}_{randNumber}'

        # Hash the password
        hashed_password = make_password(password)

        # Select company_id based on current_user_id
        company_id_query = "SELECT company_id FROM app_ofs_customuser WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(company_id_query, [current_user_id])
            company_id = cursor.fetchone()[0]

        # Insert into app_ofs_customuser
        sql_query = "INSERT INTO app_ofs_customuser (first_name, last_name, username, email, password, phone_number, userrole, added_by, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql_values = (fname, lname, username, email, hashed_password, phone, role, current_user_id, company_id)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, sql_values)

        messages.success(request, 'Staff member added successfully!')
        return HttpResponseRedirect('/staff')

    return render(request, 'staff.html')
@login_required
def getCategory(request):
    current_user_id = request.user.added_by
    sql_query = "SELECT * FROM category_info where userid = %s"

    with connection.cursor() as cursor:
        cursor.execute(sql_query, (current_user_id,))
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

@login_required
def addCategory(request):
    if request.method == 'POST':
        category_id = random.randint(1000, 9999)
        category = request.POST.get('category', None)
        current_user_id =request.user.added_by

        if category is not None:
            checkExistingCategory = "SELECT category_id FROM category_info WHERE category = %s and userid =%s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingCategory, (category, current_user_id))
                getExistingCategoryData = cursor.fetchone()
        
            if getExistingCategoryData:
                messages.info(request, 'Category Already Existed!')
                return HttpResponseRedirect('/category')


            sql_query = "INSERT INTO category_info (category_id, category, userid) VALUES (%s, %s,%s)"
            values = (category_id, category,current_user_id)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, values)
                    connection.commit()
                messages.success(request, 'Category Added successfully!')
                return HttpResponseRedirect('/category')
            except IntegrityError:
                return HttpResponse("An error occurred while adding the category")
            
        else:
            return HttpResponse("Invalid category data")
    return render(request, 'category.html')

@login_required
def editCategory(request):
    if request.method == 'POST':
        old_category_id = request.POST.get('category_id', '')
        old_category_name = request.POST.get('old_category_name', '')
        current_user_id =request.user.added_by

        sql_query = "UPDATE category_info SET category = %s WHERE category_id = %s and userid = %s"
        values = (old_category_name, old_category_id, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            messages.success(request, 'Category Edited successfully!')
            return HttpResponseRedirect('/category')
        except IntegrityError:
            return messages.error(request, 'Failed Editing Category!')
        
    return render(request, 'category.html')

@login_required
def get_categories_list(request):
    current_user_id = request.user.added_by

    categories_list = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, category FROM category_info WHERE userid =%s")
        values = (current_user_id)
        categories = cursor.fetchall()
        for category in categories:
            categories_list.append({'id': category[0], 'category': category[1]})

    return JsonResponse(categories_list, safe=False)

@login_required
def addProduct(request):
    if request.method == 'POST':
        product_id = random.randint(10000, 20000)
        getCategory = request.POST.get('product_category')
        product_name = request.POST['product_name']
        product_description = request.POST['product_description']  
        current_user_id = request.user.added_by

        if product_name:
            checkExistingProduct = "SELECT product_id FROM product_info WHERE product_name = %s and userid = %s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingProduct, (product_name,current_user_id,))
                getExistingProductData = cursor.fetchone()

        
            if getExistingProductData:
                messages.info(request, 'Product Already Existed!')
                return HttpResponseRedirect('/products')


            sql_query = "INSERT INTO product_info (product_id, product_name, product_description, category, userid) VALUES (%s, %s, %s, %s,%s)"
            values = (product_id, product_name, product_description, getCategory, current_user_id)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, values)
                    connection.commit()
                messages.success(request, 'Product Added successfully!')
                return HttpResponseRedirect('/products')
            except IntegrityError:
                return HttpResponse("An error occurred while adding the product")
            
        else:
            return HttpResponse("Invalid product data")
    return render(request, 'products.html')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_data(data, page, items_per_page=10):
    paginator = Paginator(data, items_per_page)

    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    return paginated_data



@login_required
def getProduct(request):
    current_user_id = request.user.added_by


    # Use a SQL JOIN to retrieve product information along with category names
    sql_query = """
        SELECT
            p.*,
            c.category  # Adjust this index based on the structure of your tables
        FROM
            product_info p
        LEFT JOIN
            category_info c ON p.category = c.category_id
        WHERE
            p.userid = %s
    """

    sql_query_category = "SELECT * FROM category_info WHERE userid = %s"

    with connection.cursor() as cursor:
        cursor.execute(sql_query, (current_user_id,))
        data = cursor.fetchall()

        cursor.execute(sql_query_category, (current_user_id,))
        category_data = cursor.fetchall()

    products = []
    for row in data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
            'product_description': row[3],
            'category_name': row[6],  # Assuming category name is retrieved from the JOIN
        }
        products.append(product)

    categories = []
    for row in category_data:
        category = {
            'category_id': row[1],
            'category_name': row[2],
        }
        categories.append(category)

    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'products.html', context)




@login_required
def editProduct(request):
    current_user_id = request.user.added_by

    if request.method == 'POST':
        old_product_id = request.POST.get('product_id', '')
        new_product_name = request.POST.get('new_product_name', '')
        new_product_description = request.POST.get('new_product_description', '')

        sql_query = "UPDATE product_info SET product_name = %s, product_description = %s WHERE product_id = %s and userid = %s"
        values = (new_product_name, new_product_description, old_product_id,current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            messages.info(request, 'Product Edited successfully!')
            return HttpResponseRedirect('/products')
        except IntegrityError:
            return HttpResponse("An error occurred while editing the product details")
        
    return render(request, 'products.html')

@login_required

def delete_product(request, product_id):
    current_user_id = request.user.added_by

    if request.method == 'POST':
        # Fetching the product_id from the URL parameter
        getProductID = request.POST.get('product_id', '')

        # order_query = "SELECT COUNT(*) FROM order_info WHERE product_id = %s AND status IN ('Ongoing', 'Pending') AND user_id = %s"
        order_query = "SELECT SUM(quantity) FROM order_info WHERE productid = %s AND status IN ('Ongoing', 'Pending') AND userid = %s"

        inventory_query = "SELECT SUM(quantity) FROM inventory_details WHERE productid = %s AND userid = %s"


        with connection.cursor() as cursor:
            cursor.execute(order_query, (getProductID, current_user_id))
            order_quantity = cursor.fetchone()[0] or 0  # Use 0 if the result is None

            cursor.execute(inventory_query, (getProductID, current_user_id))
            inventory_quantity = cursor.fetchone()[0] or 0  # Use 0 if the result is None


        if order_quantity > 0 or inventory_quantity > 0:
            messages.error(request, 'Products available in Order and Inventory')
            print("order_count", order_quantity)
            return JsonResponse({'status': 'error'})  # Return a JSON response on success

        sql_query = "DELETE from product_info WHERE product_id = %s and userid = %s"
        values = (getProductID, current_user_id)



        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
                print("delete," ,getProductID, current_user_id)
                messages.success(request, "Product Deleted.")
    
            return JsonResponse({'status': 'success'})  # Return a JSON response on success
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the product'})

    return render(request, 'products.html')
# from django.utils import timezone
from datetime import datetime, timedelta


@login_required

def getOrder(request):
    current_user_id = request.user.added_by

    sql_query = """
        SELECT
            o.order_id,
            o.productid,
            o.quantity,
            o.ordered_date,
            o.price,
            o.total_price,
            o.delivery_date,
            o.status,
            p.product_name
        FROM
            order_info o
        LEFT JOIN
            product_info p ON o.productid = p.product_id
        WHERE
            o.userid = %s
            AND (o.status = 'Ongoing' OR o.status = 'Pending')
    """

    values = (current_user_id,)

    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        result_set = cursor.fetchall()

        orders = []
        for row in result_set:
            order_id = row[0]
            delivery_date = row[6]
            current_date = datetime.now().date()

            # Check if the delivery_date has been surpassed today's date
            if delivery_date < current_date:
                # Update the status to 'Pending'
                update_query = "UPDATE order_info SET status = 'Pending' WHERE order_id = %s"
                cursor.execute(update_query, (order_id,))
                connection.commit()
            elif delivery_date == current_date or delivery_date > current_date:
                # Update the status to 'Ongoing'
                update_query = "UPDATE order_info SET status = 'Ongoing' WHERE order_id = %s"
                cursor.execute(update_query, (order_id,))
                connection.commit()

            order = {
                'order_id': order_id,
                'product_id': row[1],
                'quantity': row[2],
                'ordered_date': row[3],
                'price': row[4],
                'total_price': row[5], 
                'delivery_date': delivery_date,
                'status': row[7],  # Use the original status
                'product_name': row[8] if row[8] else 'Unknown Product',
            }
            orders.append(order)

        context = {
            'orders': orders,
        }

    return render(request, 'orders.html', context)
@login_required
def getCompletedOrder(request):

    current_user_id = request.user.added_by

    # Check for orders with 'Ongoing' or 'Pending' status
    sql_query = """
        SELECT
            o.order_id,
            o.productid,
            o.quantity,
            o.ordered_date,
            o.price,
            o.total_price,
            o.delivery_date,
            o.status,
            p.product_name
        FROM
            order_info o
        LEFT JOIN
            product_info p ON o.productid = p.product_id
        WHERE
            o.userid = %s
            AND (o.status = 'Completed' )
    """

    values = (current_user_id,)

    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        result_set = cursor.fetchall()

    orders = []
    for row in result_set:
        order_id = row[0]
        delivery_date = row[6]

        order = {
            'order_id': order_id,
            'product_id': row[1],
            'quantity': row[2],
            'ordered_date': row[3],
            'price': row[4],
            'total_price': row[5], 
            'delivery_date': delivery_date,
            'status': row[7],  # Use the original status
            'product_name': row[8] if row[8] else 'Unknown Product',
        }
        orders.append(order)

    context = {
        'orders': orders,
    }

    return render(request, 'completedorder.html', context)


@login_required
def getCancelledOrder(request):
    current_user_id = request.user.added_by

    # Check for orders with 'Ongoing' or 'Pending' status
    sql_query = """
        SELECT
            o.order_id,
            o.productid,
            o.quantity,
            o.ordered_date,
            o.price,
            o.total_price,
            o.delivery_date,
            o.status,
            p.product_name
        FROM
            order_info o
        LEFT JOIN
            product_info p ON o.productid = p.product_id
        WHERE
            o.userid = %s
            AND (o.status = 'Cancelled' )
    """

    values = (current_user_id,)

    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        result_set = cursor.fetchall()

    orders = []
    for row in result_set:
        order_id = row[0]
        delivery_date = row[6]

        order = {
            'order_id': order_id,
            'product_id': row[1],
            'quantity': row[2],
            'ordered_date': row[3],
            'price': row[4],
            'total_price': row[5], 
            'delivery_date': delivery_date,
            'status': row[7],  # Use the original status
            'product_name': row[8] if row[8] else 'Unknown Product',
        }
        orders.append(order)

    context = {
        'orders': orders,
    }

    return render(request, 'cancelledorder.html', context)


@login_required
def editOrder(request):
    current_user_id = request.user.added_by

    if request.method == 'POST':
        old_orderid = request.POST.get('old_orderid', '')
        edit_quantity = request.POST.get('edit_quantity', '')
        edit_price = request.POST.get('edit_price', '')
        edit_delivery_date = request.POST.get('edit_delivery_date', '')
        edit_ordered_date = request.POST.get('edit_ordered_date', '')
        edit_status = request.POST.get('edit_status', '')

        # Assuming product_id is already in the order_info table
        sql_query = "UPDATE order_info SET quantity = %s, price = %s, total_price = %s, delivery_date = %s, ordered_date =%s, status = %s WHERE order_id = %s and userid = %s"
        
        # Calculate the new total price
        total_price = float(edit_quantity) * float(edit_price)

        values = (edit_quantity, edit_price, total_price, edit_delivery_date, edit_ordered_date, edit_status, old_orderid, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/orders')
        except IntegrityError:
            return HttpResponse("An error occurred while editing the order details")

    return render(request, 'orders.html')

def order_filter(request):
    if request.method == 'POST':
        basedon = request.POST.get('basedon')
        from_date = request.POST.get('from-date')
        to_date = request.POST.get('to-date')
        max_price = request.POST.get('max-price')
        min_price = request.POST.get('min-price')
        max_quantity = request.POST.get('max-quantity')
        min_quantity = request.POST.get('min-quantity')

        sql_query = """
            SELECT *
            FROM order_info
            WHERE userid = %s
        """

        params = [request.user.added_by]

        if from_date:
            sql_query += f" AND {basedon} >= %s"
            params.append(from_date)
        if to_date:
            sql_query += f" AND {basedon} >= %s"
            params.append(to_date)
        if min_price:
            sql_query += " AND price >= %s"
            params.append(min_price)
        if max_price:
            sql_query += " AND price <= %s"
            params.append(max_price)
        if min_quantity:
            sql_query += " AND quantity >= %s"
            params.append(min_quantity)
        if max_quantity:
            sql_query += " AND quantity <= %s"
            params.append(max_quantity)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            filtered_orders = cursor.fetchall()

        filteredList = []
        for order in filtered_orders:
            context = {
                'order_id': order[1],
                'order_product_name': order[8],
                'quantity': order[2],
                'ordered_date': order[3],
                'price': order[5],
                'delivery_date': order[4],
                'status': order[6],
                'total_price':[9],
            }
            filteredList.append(context)

        return render(request, 'orders.html', {'orders': filteredList})

    return HttpResponseRedirect('/orders')

@login_required
def get_product_list(request):
    current_user_id = request.user.added_by
    sql_query_product = "SELECT id, product_name, product_id FROM product_info where userid = %s"
    values = (current_user_id)
    product_list = []
    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, values)
        products = cursor.fetchall()
        for product in products:
            product_list.append({'id': product[0], 'product': product[1], 'product_id': product[2]})

    return JsonResponse(product_list, safe=False)

from decimal import Decimal

@login_required
def addOrder(request):
    if request.method == 'POST':
        order_id = random.randint(1000, 2000)
        order_product_name = request.POST['order_product_name']
        quantity = request.POST['quantity']
        ordered_date = request.POST['ordered_date']
        delivery_date = request.POST['delivery_date']
        status = request.POST['status']
        current_user_id = request.user.added_by

        # Convert dates to datetime objects
        ordered_date = timezone.datetime.strptime(ordered_date, '%Y-%m-%d').date()
        delivery_date = timezone.datetime.strptime(delivery_date, '%Y-%m-%d').date()

        if delivery_date <= ordered_date:
            messages.error(request, 'Delivery date must be later than the order date.')
            return render(request, 'orders.html')

        # Fetch price from inventory_details based on productid
        inventory_query = "SELECT price FROM inventory_details WHERE productid = %s AND userid = %s"
        inventory_values = (order_product_name, current_user_id)

        with connection.cursor() as cursor:
            cursor.execute(inventory_query, inventory_values)
            result = cursor.fetchone()

        if result:
            price = result[0]
            # Calculate total_price
            total_price = Decimal(quantity) * Decimal(price)
        else:
            messages.error(request, 'Price not found for the specified productid.')
            price = 0
            total_price = 0
                # return render(request, 'orders.html')

        

        # Insert order information into order_info table
        sql_query = "INSERT INTO order_info (order_id, productid, quantity, ordered_date, price, total_price, delivery_date, status, userid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (order_id, order_product_name, quantity, ordered_date, price, total_price, delivery_date, status, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            previous_page = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(previous_page)
        except IntegrityError:
            return HttpResponse("An error occurred while adding the order")

    return render(request, 'orders.html')


@login_required
def delete_order(request, order_id):
    current_user_id = request.user.added_by

    if request.method == 'POST':
        sql_query = "DELETE from order_info WHERE order_id = %s and userid = %s"
        values = (order_id, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
                
            # Get the referer from the request headers
            referer = request.META.get('HTTP_REFERER')
            
            # Redirect to the referer or a default URL if referer is not available
            return HttpResponseRedirect(referer or '/default-url/')
        except IntegrityError:
            return HttpResponse("An error occurred while deleting the orders")

    return render(request, 'orders.html')

@login_required
def getProductCategory(request):
    category = request.GET.get('category')
    current_user_id =  request.user.added_by

    product_list = []
    with connection.cursor() as cursor:
        sql_query = "SELECT id, product_name, product_id FROM product_info WHERE userid =%s"
        cursor.execute(sql_query, [current_user_id])
        products = cursor.fetchall()
        # print(products)
        for product in products:
            product_list.append({'id': product[0], 'product': product[1], 'product_id': product[2]})

    return JsonResponse(product_list, safe=False)

@login_required

# def addItems(request):
#     if request.method == 'POST':
#         product = request.POST.get('getProductCategory', '')
#         quantity = request.POST.get('quantity', '')
#         price = request.POST.get('price', '')
#         current_user_id = request.user.added_by
#         current_date = timezone.now().date()

#         # Check if the entry exists in inventorydetails_date
#         existing_query_history = "SELECT product_id, quantity, price FROM inventorydetails_date WHERE product_id = %s AND date = %s AND user_id = %s"
#         existing_values_history = (product, current_date, current_user_id)

#         with connection.cursor() as cursor:
#             cursor.execute(existing_query_history, existing_values_history)
#             existing_data_history = cursor.fetchone()

#         if existing_data_history:
#             # If the entry exists, update the quantity and price in inventorydetails_date
#             updated_quantity = int(existing_data_history[1]) + int(quantity)
#             new_price = price  # You can modify this if needed

#             update_query = "UPDATE inventorydetails_date SET quantity = %s, price = %s WHERE product_id = %s AND date = %s AND user_id = %s"
#             update_values = (updated_quantity, new_price, product, current_date, current_user_id)

#             with connection.cursor() as cursor:
#                 cursor.execute(update_query, update_values)
#                 connection.commit()
#                 messages.success(request, "Inventory Updated")

#             # Now, update the price in inventory_details for today's date
#             update_query_inventory_details = "UPDATE inventory_details SET price = %s, quantity = quantity + %s WHERE productid = %s AND userid = %s"
#             update_values_inventory_details = (new_price, quantity, product, current_user_id)

#             with connection.cursor() as cursor:
#                 cursor.execute(update_query_inventory_details, update_values_inventory_details)
#                 connection.commit()

#             # Update the price in order_info for today's date
#             update_query_order_info = "UPDATE order_info SET price = %s WHERE productid = %s AND ordered_date = %s AND userid = %s"
#             update_values_order_info = (new_price, product, current_date, current_user_id)

#             with connection.cursor() as cursor:
#                 cursor.execute(update_query_order_info, update_values_order_info)
#                 connection.commit()

#             # Update total_price in order_info based on updated price and quantity
#             update_total_price_query = "UPDATE order_info SET total_price = quantity * price WHERE productid = %s AND ordered_date = %s AND userid = %s"
#             update_total_price_values = (product, current_date, current_user_id)

#             with connection.cursor() as cursor:
#                 cursor.execute(update_total_price_query, update_total_price_values)
#                 connection.commit()
#                 messages.success(request, "Price and Quantity Updated in inventory_details and order_info for today's date")

#         else:
#             # If no entry exists, insert a new row
#             insert_query = "INSERT INTO inventorydetails_date (product_id, quantity, price, user_id, date) VALUES (%s, %s, %s, %s, %s)"
#             insert_values = (product, quantity, price, current_user_id, current_date)

#             with connection.cursor() as cursor:
#                 cursor.execute(insert_query, insert_values)
#                 connection.commit()
#                 messages.success(request, "Inventory Added")

#             # Insert into inventory_details and order_info as well if needed

#     return render(request, 'inventory.html')

def addItems(request):
    if request.method == 'POST':
        product = request.POST.get('getProductCategory', '')
        quantity = request.POST.get('quantity', '')
        price = request.POST.get('price', '')
        current_user_id = request.user.added_by
        current_date = timezone.now().date()

        # Check if the entry exists in inventorydetails_date
        existing_query_history = "SELECT product_id, quantity, price FROM inventorydetails_date WHERE product_id = %s AND date = %s AND user_id = %s"
        existing_values_history = (product, current_date, current_user_id)

        with connection.cursor() as cursor:
            cursor.execute(existing_query_history, existing_values_history)
            existing_data_history = cursor.fetchone()

        if existing_data_history:
            # If the entry exists, update the quantity and price in inventorydetails_date
            updated_quantity = int(existing_data_history[1]) + int(quantity)
            new_price = price  # You can modify this if needed

            update_query = "UPDATE inventorydetails_date SET quantity = %s, price = %s WHERE product_id = %s AND date = %s AND user_id = %s"
            update_values = (updated_quantity, new_price, product, current_date, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query, update_values)
                connection.commit()
                messages.success(request, "Inventory Updated")

            # Now, update the price in inventory_details for today's date
            update_query_inventory_details = "UPDATE inventory_details SET price = %s, quantity = quantity + %s WHERE productid = %s AND userid = %s"
            update_values_inventory_details = (new_price, quantity, product, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query_inventory_details, update_values_inventory_details)
                connection.commit()

            # Update the price in order_info for today's date
            update_query_order_info = "UPDATE order_info SET price = %s WHERE productid = %s AND ordered_date = %s AND userid = %s"
            update_values_order_info = (new_price, product, current_date, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query_order_info, update_values_order_info)
                connection.commit()

            # Update total_price in order_info based on updated price and quantity
            update_total_price_query = "UPDATE order_info SET total_price = quantity * price WHERE productid = %s AND ordered_date = %s AND userid = %s"
            update_total_price_values = (product, current_date, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_total_price_query, update_total_price_values)
                connection.commit()
                # messages.success(request, "Price and Quantity Updated in inventory_details and order_info for today's date")

        else:
            # If no entry exists, insert a new row into inventorydetails_date
            insert_query = "INSERT INTO inventorydetails_date (product_id, quantity, price, user_id, date) VALUES (%s, %s, %s, %s, %s)"
            insert_values = (product, quantity, price, current_user_id, current_date)

            with connection.cursor() as cursor:
                cursor.execute(insert_query, insert_values)
                connection.commit()
                messages.success(request, "Inventory Added")

            # Check if the product_id is present in inventory_details
            existing_query_inventory_details = "SELECT productid FROM inventory_details WHERE productid = %s AND userid = %s"
            existing_values_inventory_details = (product, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(existing_query_inventory_details, existing_values_inventory_details)
                existing_data_inventory_details = cursor.fetchone()

            if not existing_data_inventory_details:
                # If product_id is not present, add a new row in inventory_details
                insert_query_inventory_details = "INSERT INTO inventory_details (productid, userid, quantity, price) VALUES (%s, %s, %s, %s)"
                insert_values_inventory_details = (product, current_user_id, quantity, price)

                try:
                    with connection.cursor() as cursor:
                        cursor.execute(insert_query_inventory_details, insert_values_inventory_details)
                        connection.commit()
                        # messages.success(request, "Added to inventory_details")

                except IntegrityError:
                    return HttpResponse("An error occurred while adding items into inventory_details")

    return render(request, 'inventory.html')

from datetime import date

@login_required
def editItems(request):
    if request.method == 'POST':
        inventory_id = request.POST.get('edit_inventory_id', '')
        product = request.POST.get('edit_getProductCategory', '')
        quantity_str = request.POST.get('edit_quantity', '')
        price = request.POST.get('edit_price', '')
        operation = request.POST.get('edit_operation', '')
        current_user_id = request.user.added_by

        try:
            quantity_change = int(quantity_str)
        except ValueError:
            messages.error(request, "Invalid quantity value")
            return redirect(request.path)  # Redirect to the same page

        existing_query_history = "SELECT product_id, quantity, date FROM inventorydetails_date WHERE id = %s AND user_id = %s"
        existing_values_history = (inventory_id, current_user_id)

        with connection.cursor() as cursor:
            cursor.execute(existing_query_history, existing_values_history)
            existing_data_history = cursor.fetchone()

        if existing_data_history:
            existing_quantity = int(existing_data_history[1])
            ordered_date = existing_data_history[2]

            if operation == 'add':
                new_quantity = existing_quantity + quantity_change
            elif operation == 'deduct':
                if quantity_change > existing_quantity:
                    messages.error(request, "Deducted quantity cannot be greater than available quantity")
                    return redirect(request.path)  # Redirect to the same page

                new_quantity = existing_quantity - quantity_change
            else:
                messages.error(request, "Invalid operation selected")
                return redirect(request.path)  # Redirect to the same page

            # If the entry exists, update the quantity and price in inventorydetails_date
            update_query_history = "UPDATE inventorydetails_date SET quantity = %s, price = %s, product_id = %s WHERE id = %s AND user_id = %s"
            update_values_history = (new_quantity, price, product, inventory_id, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query_history, update_values_history)
                connection.commit()
                messages.success(request, f"Inventory Updated.")    

                if operation == 'add':
                    update_query_inventory_details = "UPDATE inventory_details SET price = %s, quantity = quantity + %s WHERE productid = %s AND userid = %s"
                elif operation == 'deduct':
                    update_query_inventory_details = "UPDATE inventory_details SET price = %s, quantity = quantity - %s WHERE productid = %s AND userid = %s"
                else:
                    messages.error(request, "Invalid operation selected")
                    return redirect(request.path)  # Redirect to the same page

                update_values_inventory_details = (price, quantity_change, product, current_user_id)

                with connection.cursor() as cursor:
                    cursor.execute(update_query_inventory_details, update_values_inventory_details)
                    connection.commit()
                    # messages.success(request, "Price and Quantity Updated in inventory_details for today's date")

            # Now, find the corresponding entry in order_info and update the price
            update_query_order_info = "UPDATE order_info SET price = %s WHERE productid = %s AND ordered_date = %s AND userid = %s"
            update_values_order_info = (price, product, ordered_date, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query_order_info, update_values_order_info)
                connection.commit()
                # messages.success(request, f"Price Updated in order_info for ordered_date {ordered_date}")

            # Update total_price in order_info based on updated price and quantity
            update_total_price_query = "UPDATE order_info SET total_price = quantity * price WHERE productid = %s AND ordered_date = %s AND userid = %s"
            update_total_price_values = (product, ordered_date, current_user_id)

            with connection.cursor() as cursor:
                cursor.execute(update_total_price_query, update_total_price_values)
                connection.commit()
                # messages.success(request, f"Total Price Updated in order_info for ordered_date {ordered_date}")
        else:
            messages.error(request, "Inventory does not exist for editing")

        return redirect(request.path)  # Redirect to the same page

    return render(request, 'inventoryhistory.html')


@login_required
def getItems(request):
    current_user_id = request.user.added_by
    sql_query_inventory = "SELECT * FROM inventory_details where userid = %d"
    values = (current_user_id)
    with connection.cursor() as cursor:
        cursor.execute(sql_query_inventory, values)
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
                messages.success(request, "Password changed successfully!")

            return render(request, 'login.html')
        else:
            error = "Passwords do not match."
            return render(request, 'forgetpassword.html', {'otp_verified': True, 'error': error, 'email': email})
    else:
        return render(request, 'login.html')
    

@login_required
def editprofile(request):
    if request.method == 'POST':
        # Get the updated data from the form
        new_username = request.POST.get('edit_username')
        new_email = request.POST.get('edit_email')
        new_phonenumber = request.POST.get('edit_phonenumber')

        user = request.user
        changed_fields = []
        if new_username != user.username:
            user.username = new_username
            changed_fields.append('Username')

        if new_email != user.email:
            user.email = new_email
            changed_fields.append('Email')

        if new_phonenumber != user.phone_number:
            if len(new_phonenumber) == 10:
                user.phone_number = new_phonenumber
                changed_fields.append('Phone Number')
            else:
                messages.error(request, 'Phone number should be 10 digits. Please correct and try again.')
                return render(request, 'editprofile.html')
        if changed_fields:
            user.save()
            changed_fields_str = ' & '.join(changed_fields)
            messages.success(request, f'{changed_fields_str} have been updated successfully!')
        else:
            messages.info(request, 'No changes detected. Profile remains unchanged.')

    return render(request, 'editprofile.html')

# @login_required
def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('edit_old_pass')
        new_password = request.POST.get('edit_new_pass')
        confirm_password = request.POST.get('edit_confirm_pass')

        user = request.user
        email = user.email
        print(email)
        # Check if the old password matches the user's current password
        if user.check_password(old_password):
            print("checked old password")
            # Check if the new password and confirm password match
            if new_password == confirm_password:
                hashed_password = make_password(new_password)
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE app_ofs_customuser SET password = %s WHERE email = %s", [hashed_password, email])
                messages.success(request, 'Password changed successfully!')

                
                return render(request, 'changepassword.html')
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Invalid old password.')

    
    return render(request, 'changepassword.html')


@login_required
def inventorylist(request, category_name): 
    current_user_id = request.user.added_by
    sql_query = "SELECT category_id from category_info WHERE category= %s and userid =%s"
    values = (category_name,current_user_id)
    


    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        getCategoryId = cursor.fetchone()

    sql_query_product = "SELECT product_id,product_name from product_info WHERE category= %s and userid =%s"
    values_product = (getCategoryId,current_user_id) 

    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, values_product)
        product_info = cursor.fetchall()

    products = []
    for row in product_info:
        product = {
            'product_id': row[0],
            'product_name': row[1],
        }
        products.append(product)


    sql_query_product = "SELECT i.inventory_id, i.quantity, i.price, i.productid, p.product_name, p.product_id " \
                        "FROM inventory_details i " \
                        "INNER JOIN product_info p ON i.productid = p.product_id " \
                        "WHERE p.category = %s"  # Filter by category name instead of category_id
    value_inventory = (getCategoryId,)

    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, value_inventory)
        getInventoryData = cursor.fetchall()

    itemList = []
    for row in getInventoryData:
        items = {
            'inventory_id' :row[0],
            'quantity': row[1],
            'price': row[2],
            'product_id': row[3],
            'product_name': row[4],  
        }
        itemList.append(items)
   

    context = {
        'items': itemList,
        'product': products,
        'category_name': category_name
    } 
    return render(request, 'inventorylist.html', context)

@login_required
def inventoryhistory(request, category_name): 
    current_user_id = request.user.added_by
    sql_query = "SELECT category_id from category_info WHERE category= %s and userid =%s"
    values = (category_name,current_user_id)


    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        getCategoryId = cursor.fetchone()

    sql_query_product = "SELECT product_id,product_name from product_info WHERE category= %s and userid =%s"
    values_product = (getCategoryId,current_user_id) 

    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, values_product)
        product_info = cursor.fetchall()

    products = []
    for row in product_info:
        product = {
            'product_id': row[0],
            'product_name': row[1],
        }
        products.append(product)


    sql_query_product = "SELECT i.id, i.quantity, i.price, i.product_id, p.product_name, p.product_id, i.date " \
                        "FROM inventorydetails_date i " \
                        "INNER JOIN product_info p ON i.product_id = p.product_id " \
                        "WHERE p.category = %s"  # Filter by category name instead of category_id
    value_inventory = (getCategoryId,)

    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, value_inventory)
        getInventoryData = cursor.fetchall()

    itemList = []
    for row in getInventoryData:
        items = {
            'id': row[0],
            'quantity': row[1],
            'price': row[2],
            'product_id': row[5],
            'product_name': row[4],  
            'date':row[6],
        }
        itemList.append(items)
   

    context = {
        'items': itemList,
        'product': products
    } 
    return render(request, 'inventoryhistory.html', context)


   


def arima_sarimax_forecast(data, forecast_steps=12):
    # Convert 'Month' column to datetime format if not already
    data['Month'] = pd.to_datetime(data['Month'])

    # Set 'Month' as the index
    data.set_index('Month', inplace=True)

    # Perform differencing to make the time series stationary
    data_diff = data['Sales'].diff().dropna()

    # Use pmdarima to automatically choose the best parameters for ARIMA
    arima_model = pm.auto_arima(data['Sales'], seasonal=False, suppress_warnings=True, stepwise=True)
    arima_order = arima_model.get_params()['order']

    # Fit ARIMA model
    arima_result = ARIMA(data['Sales'], order=arima_order).fit()

    # Use pmdarima to automatically choose the best parameters for SARIMAX
    sarimax_model = pm.auto_arima(data['Sales'], seasonal=True, suppress_warnings=True, stepwise=True, m=12)
    sarimax_order = sarimax_model.get_params()['order']
    sarimax_seasonal_order = sarimax_model.get_params()['seasonal_order']

    # Fit SARIMAX model
    sarimax_result = sm.tsa.statespace.SARIMAX(data['Sales'], order=sarimax_order, seasonal_order=sarimax_seasonal_order).fit()

    # Forecast using ARIMA
    # arima_forecast_steps = 12
    arima_forecast = arima_result.get_forecast(steps=forecast_steps)
    arima_confidence_intervals = arima_forecast.conf_int()

    # Forecast using SARIMAX
    # sarimax_forecast_steps = 12
    sarimax_forecast = sarimax_result.get_forecast(steps=forecast_steps)
    sarimax_confidence_intervals = sarimax_forecast.conf_int()

    return {
        'arima_forecast': arima_forecast.predicted_mean,
        'arima_confidence_intervals': arima_confidence_intervals,
        'sarimax_forecast': sarimax_forecast.predicted_mean,
        'sarimax_confidence_intervals': sarimax_confidence_intervals,
    }