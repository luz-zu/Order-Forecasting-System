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

def analyze_sales(request):
    # Retrieve data from the database
    data = SalesData.objects.all().order_by('month')

    # Convert data to a pandas DataFrame
    data_df = pd.DataFrame(list(data.values('month', 'sales')))
    data_df['month'] = pd.to_datetime(data_df['month'])
    data_df.set_index('month', inplace=True)

    # Function to check stationarity using Augmented Dickey-Fuller test
    def test_stationarity(timeseries):
        # Dickey-Fuller test
        result = adfuller(timeseries, autolag='AIC')
        return result[0], result[1], result[4]

    # Plot original time series
    plt.figure(figsize=(10, 6))
    plt.plot(data_df['sales'])
    plt.title('Original Time Series')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.grid(True)
    plt.tight_layout()
    original_plot = get_image()

    # Check stationarity
    adf_statistic, p_value, critical_values = test_stationarity(data_df['sales'])
    stationarity_result = f'ADF Statistic: {adf_statistic}\n p-value: {p_value}\n Critical Values: {critical_values}'

    # Perform differencing to make the time series stationary
    data_diff = data_df['sales'].diff().dropna()

    # Plot differenced time series
    plt.figure(figsize=(10, 6))
    plt.plot(data_diff)
    plt.title('Differenced Time Series')
    plt.xlabel('Month')
    plt.ylabel('Sales Difference')
    plt.grid(True)
    plt.tight_layout()
    differenced_plot = get_image()

    # Check stationarity of differenced time series
    adf_statistic_diff, p_value_diff, critical_values_diff = test_stationarity(data_diff)
    stationarity_result_diff = f'ADF Statistic: {adf_statistic_diff}\n p-value: {p_value_diff}\n Critical Values: {critical_values_diff}'

    # Calculate autocorrelation and partial autocorrelation functions
    lag_acf = acf(data_diff, nlags=20)
    lag_pacf = pacf(data_diff, nlags=20, method='ols')

    # Plot ACF
    plt.figure(figsize=(12, 4))
    plt.subplot(121)
    plt.stem(range(1, len(lag_acf) + 1), lag_acf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.title('Autocorrelation Function')

    # Plot PACF
    plt.subplot(122)
    plt.stem(range(1, len(lag_pacf) + 1), lag_pacf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.title('Partial Autocorrelation Function')

    acf_pacf_plot = get_image()

    # Use pmdarima to automatically choose the best parameters for ARIMA
    arima_model = pm.auto_arima(data_df['sales'], seasonal=False, suppress_warnings=True, stepwise=True)
    arima_order = arima_model.get_params()['order']

    # Fit ARIMA model
    arima_result = ARIMA(data_df['sales'], order=arima_order).fit()

    # Print ARIMA model summary
    arima_model_summary = arima_result.summary()

    # Use pmdarima to automatically choose the best parameters for SARIMAX
    sarimax_model = pm.auto_arima(data_df['sales'], seasonal=True, suppress_warnings=True, stepwise=True, m=12)
    sarimax_order = sarimax_model.get_params()['order']
    sarimax_seasonal_order = sarimax_model.get_params()['seasonal_order']

    # Fit SARIMAX model
    sarimax_result = sm.tsa.statespace.SARIMAX(data_df['sales'], order=sarimax_order, seasonal_order=sarimax_seasonal_order).fit()

    # Print SARIMAX model summary
    sarimax_model_summary = sarimax_result.summary()

    # Forecast using ARIMA
    arima_forecast_steps = 30
    arima_forecast = arima_result.get_forecast(steps=arima_forecast_steps)
    arima_confidence_intervals = arima_forecast.conf_int()

    # Forecast using SARIMAX
    sarimax_forecast_steps = 30
    sarimax_forecast = sarimax_result.get_forecast(steps=sarimax_forecast_steps)
    sarimax_confidence_intervals = sarimax_forecast.conf_int()

    # Plot the ARIMA and SARIMAX forecasts
    plt.figure(figsize=(12, 6))
    plt.plot(data_df['sales'], label='Actual')
    plt.plot(arima_forecast.predicted_mean, color='red', label='ARIMA Forecast')
    plt.fill_between(arima_confidence_intervals.index, arima_confidence_intervals.iloc[:, 0], arima_confidence_intervals.iloc[:, 1], color='pink', alpha=0.3, label='ARIMA Confidence Intervals')
    plt.plot(sarimax_forecast.predicted_mean, color='blue', label='SARIMAX Forecast')
    plt.fill_between(sarimax_confidence_intervals.index, sarimax_confidence_intervals.iloc[:, 0], sarimax_confidence_intervals.iloc[:, 1], color='lightblue', alpha=0.3, label='SARIMAX Confidence Intervals')
    plt.title('ARIMA and SARIMAX Forecasts')
    plt.legend()
    forecast_plot = get_image()
# return render(request, 'dashboard/dashboard.html', context)
    # Render the results
    return render(request, 'dashboard/dashboard.html', {
        'original_plot': original_plot,
        'stationarity_result': stationarity_result,
        'differenced_plot': differenced_plot,
        'stationarity_result_diff': stationarity_result_diff,
        'acf_pacf_plot': acf_pacf_plot,
        'arima_model_summary': arima_model_summary,
        'sarimax_model_summary': sarimax_model_summary,
        'forecast_plot': forecast_plot,
    })

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
            return render(request, 'login.html', {'error': 'Invalid Username or Password'})
    return render(request, 'login.html')

@not_logged_in
@never_cache
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You are now logged in.')
            return render(request, 'register.html',  {'form': form})
        else:
            messages.error(request, 'Registration failed. Please check the provided information.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
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
    current_user_id = request.user.id
    sql_category = "SELECT * FROM category_info where userid = %s"

    sql_product = "SELECT * FROM product_info where userid = %s"
    value = (current_user_id,)
    with connection.cursor() as cursor:
        cursor.execute(sql_category, value)
        data = cursor.fetchall()
        cursor.execute(sql_product, value)
        product_data = cursor.fetchall()


    products = []
    for row in product_data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
            'product_description': row[3],
            'category': row[4],
        }
        products.append(product)

    categories = []
    for row in data:
        category = {
            'category_id': row[1],  # Assuming category_id is in the first column (index 0)
            'category': row[2],     # Assuming category name is in the second column (index 1)
        }
        categories.append(category)
    context = {
        'categories': categories,
        'products':products,
    }

    return render(request, 'inventory.html', context)

@login_required
def staff(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM app_ofs_customuser where userrole = 'staff'")
        staff_members = cursor.fetchall()
    
    staff_details = []
    for row in staff_members:
        staff = {
            'fname': row[5],
            'lname': row[6],
            'username': row[4],
            'email': row[7],
            'phone': row[12],
            'role': row[16],
        }
        staff_details.append(staff)
    
    context = {
        'staff_members': staff_details
    }
    return render(request, 'staff.html', context)

@login_required
def addStaff(request):
    if request.method == 'POST':
        fname = request.POST.get('first_name', '')
        lname = request.POST.get('last_name', '')
        email = request.POST.get('staff_email', '')
        password = 'pbkdf2_sha256$720000$mxe0Xh0bzkxMDPfH0eJWID$OtcNwAuQDGiT1ulQSIlK3wosxBmdwH3qKb31UJOCGCA=' # ofs@12345
        phone = request.POST.get('staff_phone', '')
        role = request.POST.get('staff_role', '')

        randNumber = random.randint(100, 999)
        username = f'{fname.lower()}_{randNumber}'

        sql_query = "INSERT INTO app_ofs_customuser (first_name, last_name, username, email, password, phone_number, userrole) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        sql_values = (fname, lname, username, email, password, phone, role)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, sql_values)

        return HttpResponseRedirect('/staff')

    return render(request, 'staff.html')

@login_required
def getCategory(request):
    current_user_id = request.user.id
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
        current_user_id =request.user.id

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
        current_user_id =request.user.id

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
    current_user_id = request.user.id

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
        current_user_id = request.user.id

        if product_name:
            checkExistingProduct = "SELECT product_id FROM product_info WHERE product_name = %s and userid = %s"
            with connection.cursor() as cursor:
                cursor.execute(checkExistingProduct, (product_name,current_user_id,))
                getExistingProductData = cursor.fetchone()

        
            if getExistingProductData:
                return HttpResponse("Product already exists")


            sql_query = "INSERT INTO product_info (product_id, product_name, product_description, category, userid) VALUES (%s, %s, %s, %s,%s)"
            values = (product_id, product_name, product_description, getCategory, current_user_id)

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




@login_required
def getProduct(request):
    current_user_id = request.user.id
    sql_query_product = "SELECT * FROM product_info where userid = %s"
    sql_query_category = "SELECT * FROM category_info where userid = %s"

    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, (current_user_id,))
        data = cursor.fetchall()

        cursor.execute(sql_query_category, (current_user_id,))
        category_data = cursor.fetchall()

    products = []
    for row in data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
            'product_description': row[3],
            'category': row[4],           
        }
        products.append(product)
      

    categories = []
    for row in category_data:
        category = {
            'category_id': row[1],  # Assuming category_id is in the first column (index 0)
            'category': row[2],     # Assuming category name is in the second column (index 1)
        }
        categories.append(category)
    context = {
        'categories': categories,
        'products': products,
    }

    # print(context_category)

    return render(request, 'products.html', context)

@login_required
def editProduct(request):
    current_user_id = request.user.id

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

            return HttpResponseRedirect('/products')
        except IntegrityError:
            return HttpResponse("An error occurred while editing the product details")
        
    return render(request, 'products.html')

@login_required
def delete_product(request, product_id):
    current_user_id = request.user.id
    if request.method == 'POST':
        getProductID = request.POST.get('product_id', '')

        sql_query = "DELETE from product_info WHERE product_id = %s and userid = %s"
        values = (getProductID, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
                messages.success(request, "Product Deleted.")
    
            return HttpResponseRedirect('/products')
        except IntegrityError:
            return HttpResponse("An error occurred while deleting the products")
        
        
    return render(request, 'products.html')

@login_required
def getOrder(request):
    current_user_id = request.user.id
    sql_query_order = "SELECT * FROM order_info WHERE userid = %s AND (status = 'Ongoing' OR status = 'Pending')"

    values_order = (current_user_id)
    sql_query_product = "SELECT * FROM product_info WHERE userid = %s"
    values_product = (current_user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql_query_order, values_order)
        data = cursor.fetchall()

        cursor.execute(sql_query_product, values_product)
        product_data = cursor.fetchall()

    orders = []
    for row in data:
        order = {
            'order_id': row[1],
            'order_product_name': row[7],
            'quantity': row[2],
            'ordered_date': row[3],
            'price': row[5],
            'delivery_date': row[4],
            'status': row[6],
        }
        orders.append(order)

    products = []
    for row in product_data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
        }
        products.append(product)
    context = {
        'orders': orders,
        'products': products,

    }

    return render(request, 'orders.html', context)


@login_required
def getCompletedOrder(request):
    current_user_id = request.user.id
    sql_query_order = "SELECT * FROM order_info WHERE userid = %s AND (status = 'Completed') ORDER BY ordered_date DESC LIMIT 2"

    values_order = (current_user_id)
    sql_query_product = "SELECT * FROM product_info WHERE userid = %s"
    values_product = (current_user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql_query_order, values_order)
        data = cursor.fetchall()

        cursor.execute(sql_query_product, values_product)
        product_data = cursor.fetchall()

    orders = []
    for row in data:
        order = {
            'order_id': row[1],
            'order_product_name': row[7],
            'quantity': row[2],
            'ordered_date': row[3],
            'price': row[5],
            'delivery_date': row[4],
            'status': row[6],
        }
        orders.append(order)

    products = []
    for row in product_data:
        product = {
            'product_id': row[1],
            'product_name': row[2],
        }
        products.append(product)
    context = {
        'orders': orders,
        'products': products,

    }

    return render(request, 'getCompletedOrder.html', context)

@login_required
def editOrder(request):
    current_user_id = request.user.id
    if request.method == 'POST':
        old_orderid = request.POST.get('old_orderid', '')
        edit_quantity = request.POST.get('edit_quantity', '')
        edit_price = request.POST.get('edit_price', '')
        edit_delivery_date = request.POST.get('edit_delivery_date', '')
        edit_status = request.POST.get('edit_status', '')

        sql_query = "UPDATE order_info SET quantity = %s, price = %s, delivery_date = %s, status = %s WHERE order_id = %s and userid = %s"
        values = (edit_quantity, edit_price, edit_delivery_date, edit_status, old_orderid, current_user_id)

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

        params = [request.user.id]

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
            }
            filteredList.append(context)

        return render(request, 'orders.html', {'orders': filteredList})

    return HttpResponseRedirect('/orders')

@login_required
def get_product_list(request):
    current_user_id = request.user.id
    sql_query_product = "SELECT id, product_name FROM product_info where userid = %s"
    values = (current_user_id)
    product_list = []
    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, values)
        products = cursor.fetchall()
        for product in products:
            product_list.append({'id': product[0], 'product': product[1]})

    return JsonResponse(product_list, safe=False)

@login_required
def addOrder(request):
    if request.method == 'POST':
        order_id = random.randint(1000, 2000)
        order_product_name = request.POST['order_product_name']
        quantity = request.POST['quantity']
        ordered_date = request.POST['ordered_date']
        price = request.POST['price']
        delivery_date = request.POST['delivery_date']
        status = request.POST['status']
        current_user_id = request.user.id

        ordered_date = timezone.datetime.strptime(ordered_date, '%Y-%m-%d').date()
        delivery_date = timezone.datetime.strptime(delivery_date, '%Y-%m-%d').date()

        if delivery_date <= ordered_date:
            error_message = "Delivery date must be later than the order date."

            return HttpResponse("Delivery date must be later than the order date.")

        sql_query = "INSERT INTO order_info (order_id, productid, quantity, ordered_date, price, delivery_date, status, userid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (order_id, order_product_name, quantity,ordered_date , price, delivery_date, status, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()
            previous_page = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(previous_page)
        except IntegrityError:
            return HttpResponse("An error occurred while adding the product")
            
    return render(request, 'orders.html', {'error_message':error_message})





@login_required
def delete_order(request, order_id):
    current_user_id =  request.user.id
    if request.method == 'POST':
        getOrderID = request.POST.get('order_id', '')
        sql_query = "DELETE from order_info WHERE order_id = %s and userid = %s"
        values = (getOrderID, current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/orders')
        except IntegrityError:
            return HttpResponse("An error occurred while deleting the orders")
        
    return render(request, 'orders.html')

@login_required
def getProductCategory(request):
    category = request.GET.get('category')
    current_user_id =  request.user.id

    product_list = []
    with connection.cursor() as cursor:
        sql_query = "SELECT id, product_name FROM product_info WHERE category = %s and userid =%s"
        cursor.execute(sql_query, [category, current_user_id])
        products = cursor.fetchall()
        # print(products)
        for product in products:
            # print(product[1])
            product_list.append({'id': product[0], 'product': product[1]})

    return JsonResponse(product_list, safe=False)

@login_required
def addItems(request):
    if request.method == 'POST':
        product = request.POST.get('getProductCategory', '')
        quantity = request.POST.get('quantity', '')
        price = request.POST.get('price', '')
        current_user_id = request.user.id

        new_query = "SELECT product_name from product_info WHERE product_name = %s and userid = %s"
        values = (product,current_user_id,)

        with connection.cursor() as cursor:
            cursor.execute(new_query, values)
            getCategoryId = cursor.fetchone()
        
            print("Product Name", getCategoryId)

        sql_query = "INSERT INTO inventory_details (productid, quantity, price, categoryid, userid) VALUES (%s, %s, %s,%s,%s)"
        values = (product, quantity, price, getCategoryId,current_user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

            return HttpResponseRedirect('/inventory')
        except IntegrityError:
            return HttpResponse("An error occurred while adding items into the inventory")

    return render(request, 'inventory.html')

@login_required
def getItems(request):
    current_user_id = request.user.id
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

@login_required
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
            user.phone_number = new_phonenumber
            changed_fields.append('Phone Number')

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
    current_user_id = request.user.id
    sql_query = "SELECT category_id from category_info WHERE category= %s and userid =%s"
    values = (category_name,current_user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        getCategoryId = cursor.fetchone()
    print("pro", getCategoryId)
    sql_query_product = "SELECT i.quantity, i.price, i.productid, p.product_name " \
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
            'quantity': row[0],
            'price': row[1],
            'product_name': row[3],  # Index 3 holds the product_name
        }
        itemList.append(items)

    context = {
        'items': itemList,
    } 
    return render(request, 'inventorylist.html', context)


    # sql_query_product = "SELECT * from inventory_details WHERE categoryid= %s"
    # value_inventory = (getCategoryId,)

    # sql_query_product = "SELECT i.quantity, i.price, i.productid, i.categoryid, p.product_name " \
    #                         "FROM inventory_details i " \
    #                         "INNER JOIN product_info p ON i.productid = p.product_id " \
    #                         "WHERE i.categoryid = %s"
    # value_inventory = (getCategoryId,)

    # with connection.cursor() as cursor:
    #     cursor.execute(sql_query_product, value_inventory)
    #     getInventoryData = cursor.fetchall()
    # print(getInventoryData)

    # itemList = []
    # for row in getInventoryData:
    #     items = {
    #         'quantity': row[0],
    #         'price': row[1],
    #         'product_name': row[4],
    #     }
    #     itemList.append(items)

    # context = {
    #     'items': itemList,
    # } 
    # return render(request, 'inventorylist.html', context)

