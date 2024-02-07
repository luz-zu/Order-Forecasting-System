from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout,update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseNotFound
from django.http import JsonResponse
from .forms import RegisterForm,ProductForm, AddInventoryForm, EditInventoryForm
from django.db import connection, IntegrityError, transaction
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Sum ,F, Count,Max,Q,ExpressionWrapper, IntegerField,Subquery, OuterRef,Q


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
import datetime
from django.db.models import F, Func, ExpressionWrapper, DateField
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta

@login_required


# old code
# def user_dashboard(request):
#     # Fetch the last 12 months and future 12 months forecast data if available
#     current_date = datetime.now().date()
#     current_month = current_date.replace(day=1)
#     last_12_months = current_date - relativedelta(months=12)
#     next_12_months = current_date + relativedelta(months=12)
 
#     forecast_data_next_12_months_exists = ForecastData.objects.filter(ordered_date__gte=current_month, ordered_date__lte=next_12_months).order_by('ordered_date')
#     forecast_data_queryset = ForecastData.objects.filter(ordered_date__gte=last_12_months, ordered_date__lte=next_12_months).order_by('ordered_date')
#     actual_data = ForecastData.objects.filter(ordered_date__lt=current_date -relativedelta(months=1), ordered_date__gte=last_12_months).order_by('ordered_date')

#     if not forecast_data_next_12_months_exists.exists():
#         # Perform ARIMA or SARIMAX forecast if data doesn't exist in the given range
#         data_queryset = ForecastData.objects.all().values('ordered_date', 'quantity')
#         data = pd.DataFrame(data_queryset)
#         data.columns = ["Month", "Sales"]
#         data = data.dropna()

#         results = arima_sarimax_forecast(data)
#         print(results)
#         results_df = pd.DataFrame()

#         for method, values in results.items():
#             if method == 'sarimax_forecast':
#                 dates = list(values.index)
#                 forecast_values = list(values.values)
#                 results_df['Dates'] = dates
#                 results_df['Forecast_Values'] = forecast_values
#             elif method == 'sarimax_confidence_intervals':
#                 upper_ci = list(values['upper Sales'])
#                 lower_ci = list(values['lower Sales'])
#                 results_df['Upper_CI'] = upper_ci
#                 results_df['Lower_CI'] = lower_ci

#         # Print the DataFrame to verify
#         print(results_df)
#         results_df['Dates'] = pd.to_datetime(results_df['Dates']).dt.date

#         for index, row in results_df.iterrows():
#             date = row['Dates']
#             forecast_value = row['Forecast_Values']
#             lower_ci = row['Lower_CI']
#             upper_ci = row['Upper_CI']
            

#             # Check if data already exists for this date
#             existing_data = ForecastData.objects.filter(ordered_date=date.strftime('%Y-%m-%d'))

#             if existing_data.exists():
#                 # Update existing data
#                 existing_data.update(
#                     forecasted_quantity=forecast_value,
#                     lower_ci_sarimax=lower_ci,
#                     upper_ci_sarimax=upper_ci
#                 )
#             else:
#                 # Create new data
#                 ForecastData.objects.create(
#                     quantity=0,
#                     ordered_date=date,
#                     forecasted_quantity=forecast_value,
#                     lower_ci_sarimax=lower_ci,
#                     upper_ci_sarimax=upper_ci
#                 )

#     forecast_dates = [forecast.ordered_date.strftime("%b %Y") for forecast in forecast_data_queryset]
#     forecast_quantity = [forecast.forecasted_quantity for forecast in forecast_data_queryset]
#     upper_ci_sarimax = [forecast.upper_ci_sarimax for forecast in forecast_data_queryset]
#     lower_ci_sarimax = [forecast.lower_ci_sarimax for forecast in forecast_data_queryset]
#     actual_quantity = [actual.quantity for actual in actual_data]

#     # Create SARIMAX chart
#     sarimax_chart = go.Figure()

#     # Plot actual data if available
#     if actual_quantity:
#         sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=actual_quantity, mode='lines', name='Actual Sales'))

#     # Plot forecast data and confidence intervals
#     sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=forecast_quantity, mode='lines', name='SARIMAX Forecast'))
#     sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=upper_ci_sarimax, mode='lines', name='SARIMAX Upper CI'))
#     sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=lower_ci_sarimax, mode='lines', name='SARIMAX Lower CI'))

#     sarimax_chart.update_layout(title='SARIMAX Forecast with Confidence Intervals')

#     # Convert SARIMAX chart to HTML
#     sarimax_chart_html = sarimax_chart.to_html(full_html=False)

#     context = {
#         'sarimax_chart_html': sarimax_chart_html,
#     }

#     return render(request, 'dashboard/dashboard.html', context)

# correct code
def user_dashboard(request):
    # Fetch the last 12 months and future 12 months forecast data if available
    current_date = datetime.now().date()
    # current_date = datetime(2024, 5, 1).date()
    current_month = current_date.replace(day=1)
    last_12_months = current_date - relativedelta(months=12)
    next_12_months = current_date + relativedelta(months=12)
    
    # Check if there's any missing data in the next 12 months (excluding the current month)
    missing_data_exists = any(not ForecastData.objects.filter(ordered_date=current_month + relativedelta(months=i)).exists() for i in range(1, 13) if current_month + relativedelta(months=i) != current_month)

    if missing_data_exists:
        # Perform ARIMA or SARIMAX forecast if data doesn't exist in the given range
        data_queryset = ForecastData.objects.all().values('ordered_date', 'quantity')
        data = pd.DataFrame(data_queryset)
        data.columns = ["Month", "Sales"]
        data = data.dropna()

        results = arima_sarimax_forecast(data)
        results_df = pd.DataFrame()

        for method, values in results.items():
            if method == 'sarimax_forecast':
                dates = list(values.index)
                forecast_values = list(values.values)
                results_df['Dates'] = dates
                results_df['Forecast_Values'] = forecast_values
            elif method == 'sarimax_confidence_intervals':
                upper_ci = list(values['upper Sales'])
                lower_ci = list(values['lower Sales'])
                results_df['Upper_CI'] = upper_ci
                results_df['Lower_CI'] = lower_ci

        # Print the DataFrame to verify
        print(results_df)
        results_df['Dates'] = pd.to_datetime(results_df['Dates']).dt.date

        for index, row in results_df.iterrows():
            date = row['Dates']
            forecast_value = row['Forecast_Values']
            lower_ci = row['Lower_CI']
            upper_ci = row['Upper_CI']

            # Check if data already exists for this date
            existing_data = ForecastData.objects.filter(ordered_date=date.strftime('%Y-%m-%d'))

            # Do not update data for current month
            if existing_data.exists() and date.month != current_date.month:
                # Update existing data
                existing_data.update(
                    forecasted_quantity=forecast_value,
                    lower_ci_sarimax=lower_ci,
                    upper_ci_sarimax=upper_ci
                )
            elif not existing_data.exists():
                # Create new data
                ForecastData.objects.create(
                    quantity=0,
                    ordered_date=date,
                    forecasted_quantity=forecast_value,
                    lower_ci_sarimax=lower_ci,
                    upper_ci_sarimax=upper_ci
                )

    # Fetch updated forecast data queryset after potential updates
    forecast_data_queryset = ForecastData.objects.filter(ordered_date__gte=last_12_months, ordered_date__lte=next_12_months).order_by('ordered_date')
    actual_data = ForecastData.objects.filter(ordered_date__lt=current_date - relativedelta(months=1), ordered_date__gte=last_12_months).order_by('ordered_date')

    actual_quantity = [actual.quantity for actual in actual_data]

    forecast_dates = [forecast.ordered_date.strftime("%b %Y") for forecast in forecast_data_queryset]
    forecast_quantity = [forecast.forecasted_quantity for forecast in forecast_data_queryset]
    upper_ci_sarimax = [forecast.upper_ci_sarimax for forecast in forecast_data_queryset]
    lower_ci_sarimax = [forecast.lower_ci_sarimax for forecast in forecast_data_queryset]

    # Create SARIMAX chart
    sarimax_chart = go.Figure()

    # Plot actual data if available
    if actual_quantity:
        sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=actual_quantity, mode='lines', name='Actual Sales'))

    # Plot forecast data and confidence intervals
    sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=forecast_quantity, mode='lines', name='SARIMAX Forecast'))
    sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=upper_ci_sarimax, mode='lines', name='SARIMAX Upper CI'))
    sarimax_chart.add_trace(go.Scatter(x=forecast_dates, y=lower_ci_sarimax, mode='lines', name='SARIMAX Lower CI'))

    sarimax_chart.update_layout(title='SARIMAX Forecast with Confidence Intervals')

    # Convert SARIMAX chart to HTML
    sarimax_chart_html = sarimax_chart.to_html(full_html=False)

    context = {
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

# def inventory(request):
#     current_user_id = request.user.added_by
  
#     sql_category_with_count = """
#         SELECT
#             c.id,
#             c.category,
#             COUNT(p.product_id) AS total_products
#         FROM
#             category_info c
#         LEFT JOIN
#             product_info p ON c.id = p.category_id
#         WHERE
#             c.userid_id = %s
#         GROUP BY
#             c.id, c.category
#     """

#     value = (current_user_id,)
#     with connection.cursor() as cursor:
#         cursor.execute(sql_category_with_count, value)
#         categories_with_count = cursor.fetchall()

#     categories = []
#     for row in categories_with_count:
#         category_id = row[0]
#         category_name = row[1]
#         total_products = row[2]

#         # Only include categories with a count greater than 0
#         if total_products > 0:
#             category = {
#                 'category_id': category_id,
#                 'category': category_name,
#                 'total_products': total_products,
#             }
#             categories.append(category)

#     context = {
#         'categories': categories,
#     }
   
#     return render(request, 'inventory.html', context)


def inventory(request):
    current_user = request.user

    # Filter products where deleted_on is NULL
    categories_with_count = category.objects.filter(userid_id=current_user).annotate(
        total_products=Count('product_info', filter=Q(product_info__deleted_on__isnull=True))
    ).values('id', 'category', 'total_products')

    search_query = request.GET.get('q')
    

    categories = []
    for row in categories_with_count:
        category_id = row['id']
        category_name = row['category']
        total_products = row['total_products']

        if search_query:
            if search_query.lower() not in category_name.lower():
                continue  # Skip categories that don't match the search query

        # Only include categories with a count greater than 0
        if total_products > 0:
            category_item = {
                'category_id': category_id,
                'category': category_name,
                'total_products': total_products,
            }
            categories.append(category_item)

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


# def addStaff(request):
#     if request.method == 'POST':
#         # Get current user ID
#         current_user_id = request.user.id if request.user.is_authenticated else None

#         fname = request.POST.get('first_name', '')
#         lname = request.POST.get('last_name', '')
#         email = request.POST.get('staff_email', '')
#         password = 'ofs@12345'  # Note: You may want to generate a secure password
#         phone = request.POST.get('staff_phone', '')
#         role = request.POST.get('staff_role', '')

#         # Validate phone number length
#         if len(phone) != 10:
#             messages.error(request, 'Phone number must be 10 digits.')
#             return HttpResponseRedirect('/staff')

#         # Check if the email already exists
#         email_exists_query = "SELECT COUNT(*) FROM app_ofs_customuser WHERE email = %s"
#         email_exists_values = (email,)

#         with connection.cursor() as cursor:
#             cursor.execute(email_exists_query, email_exists_values)
#             email_count = cursor.fetchone()[0]

#         if email_count > 0:
#             messages.error(request, 'Email already exists. Please use a different email address.')
#             return HttpResponseRedirect('/staff')

#         # Generate a random username
#         randNumber = random.randint(100, 999)
#         username = f'{fname.lower()}_{randNumber}'

#         # Hash the password
#         hashed_password = make_password(password)

#         # Select company_id based on current_user_id
#         company_id_query = "SELECT company_id FROM app_ofs_customuser WHERE id = %s"
#         with connection.cursor() as cursor:
#             cursor.execute(company_id_query, [current_user_id])
#             company_id = cursor.fetchone()[0]

#         # Insert into app_ofs_customuser
#         sql_query = "INSERT INTO app_ofs_customuser (first_name, last_name, username, email, password, phone_number, userrole, added_by, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
#         sql_values = (fname, lname, username, email, hashed_password, phone, role, current_user_id, company_id)

#         with connection.cursor() as cursor:
#             cursor.execute(sql_query, sql_values)

#         messages.success(request, 'Staff member added successfully!')
#         return HttpResponseRedirect('/staff')

#     return render(request, 'staff.html')

def addStaff(request):
    if request.method == 'POST':
        current_user = request.user

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

        try:
            # Create a new CustomUser (staff member)
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=fname,
                last_name=lname,
                phone_number=phone,
                userrole=role,
                added_by=current_user
            )

            messages.success(request, 'Staff member added successfully!')
            return HttpResponseRedirect('/staff')

        except IntegrityError:
            messages.error(request, 'Email already exists. Please use a different email address.')
            return HttpResponseRedirect('/staff')

    return render(request, 'staff.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from .models import category, Product, InventoryDetails, InventoryDetailsDate, Order,CustomUser,ForecastData
from .forms import CategoryForm
from django.contrib.auth.decorators import login_required
from django.core.management.base import BaseCommand



@login_required
# def get_category(request):
#     current_user_id = request.user.added_by
#     categories = category.objects.filter(userid=current_user_id)
#     page = request.GET.get('page', 1)

#     # Paginate the products with 20 items per page
#     paginated_products = paginate_data(categories, page, 20)

#     context = {'categories': paginated_products,
#                'category': categories}
#     return render(request, 'category.html', context)

# def get_category(request):
#     current_user_id = request.user.added_by
#     categories = category.objects.filter(userid=current_user_id)
#     search_query = request.GET.get('q')

#     if search_query:
#         categories = categories.filter(Q(category__icontains=search_query))

#     page = request.GET.get('page', 1)
#     paginated_products = paginate_data(categories, page, 20)

#     context = {
#         'categories': paginated_products,
#         'category': categories,
#         'search_query': search_query,  # Pass search query back to the template
#     }
#     return render(request, 'category.html', context)

def get_category(request):
    current_user_id = request.user.added_by
    categories = category.objects.filter(userid=current_user_id)
    search_query = request.GET.get('q')

    if search_query:
        categories = categories.filter(Q(category__icontains=search_query) | Q(id__icontains=search_query))
    page = request.GET.get('page', 1)
    paginated_products = paginate_data(categories, page, 20)

    context = {
        'categories': paginated_products,
        'search_query': search_query,  # Pass search query back to the template
    }
    return render(request, 'category.html', context)

@login_required

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category'].capitalize()
            current_user = request.user  # Assuming request.user is a CustomUser instance
            if not category_name:
                messages.error(request, 'Category cannot be empty.')
                return redirect('category')

            # Check if a category with the lowercase name already exists
            existing_category = category.objects.filter(category__iexact=category_name, userid=current_user).first()

            if existing_category:
                messages.error(request, 'Category already exists!')
            else:
                try:
                    category.objects.create(category=category_name, userid=current_user)
                    messages.success(request, 'Category added successfully!')
                except IntegrityError:
                    messages.error(request, 'An error occurred while adding the category.')

            return redirect('category')
        
        else:
            return redirect('category')

    else:
        form = CategoryForm()

    return render(request, 'category.html', {'form': form})

@login_required
def edit_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            old_category_id = form.cleaned_data['category_id']
            old_category_name = form.cleaned_data['old_category_name'].capitalize()
            current_user_id = request.user.added_by

            if not old_category_name:
                messages.error(request, 'Category cannot be empty.')
                return redirect('category')

            try:
                category_instance = category.objects.get(id=old_category_id, userid=current_user_id)
                
                # Check if the new name is different
                if old_category_name == category_instance.category:
                    messages.warning(request, 'No changes made to the category.')
                    return redirect('category')

                # Check if the new name already exists for other products
                if category.objects.filter(category__iexact=old_category_name).exclude(id=old_category_id).exists():
                    messages.error(request, 'Category name already exists for another product.')
                    return redirect('category')

                category_instance.category = old_category_name
                category_instance.save()

                messages.success(request, 'Category edited successfully!')
            except category.DoesNotExist:
                messages.error(request, 'Category not found!')
            except IntegrityError:
                messages.error(request, 'Failed editing category!')
            except ValidationError as e:
                messages.error(request, e.message)

            return redirect('category')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CategoryForm()

    return render(request, 'category.html', {'form': form})

@login_required
def get_categories_list(request):
    current_user_id = request.user.added_by
    categories_list = category.objects.filter(userid_id=current_user_id).values('id', 'category')

    return JsonResponse(list(categories_list), safe=False)

def paginate_data(data, page_number, items_per_page):
    paginator = Paginator(data, items_per_page)

    try:
        paginated_data = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    return paginated_data

@login_required
def getProduct(request):
    current_user = request.user

    products = Product.objects.filter(user_id=current_user, deleted_on__isnull=True).order_by('-id')
    categories = category.objects.filter(userid_id=current_user)
    search_query = request.GET.get('q')

    if search_query:
        products = products.filter(
            Q(product_id__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query) |
           Q(category__category__icontains=search_query)
        )

    
    # Get the page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Paginate the products with 20 items per page
    paginated_products = paginate_data(products, page, 20)

    context = { 
        'products': paginated_products,
        'categories': categories,
    }
    
    return render(request, 'products.html', context)

@login_required
def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_name'].capitalize()
            product_description = form.cleaned_data['product_description']
            current_user = request.user

            if not product_name:
                messages.error(request, 'Product name cannot be blank')
                return HttpResponseRedirect('/products')

            existing_product = Product.objects.filter(
                product_name=product_name,
                user=current_user,
                deleted_on__isnull=False
            ).first()

            if existing_product:
                existing_product.deleted_on = None
                existing_product.save()
                messages.success(request, 'Product added successfully!')
            else:
                existing_product = Product.objects.filter(
                    product_name=product_name,
                    user=current_user,
                    deleted_on__isnull=True
                ).first()

                if existing_product:
                    messages.info(request, 'Product already exists!')
                else:
                    max_product_id = Product.objects.filter(user=current_user).aggregate(Max('product_id'))['product_id__max']
                    if max_product_id is not None:
                # Increment the product ID for a new product
                        form.instance.product_id = int(max_product_id) + 1
                    else:
                # Set initial product_id to 101 if no existing products
                        form.instance.product_id =  101
                    category_name = request.POST.get('product_category')
                    
                    try:
                        category_instance = category.objects.get(category=category_name, userid_id=current_user)
                        form.instance.category_id = category_instance.id
                    except category.DoesNotExist:
                        messages.error(request, 'Category not found!')
                        return HttpResponseRedirect('/products')

                    form.instance.user = current_user
                    form.cleaned_data['product_name'] = product_name
                    form.save()

                    messages.success(request, 'Product added successfully!')

            return HttpResponseRedirect('/products')
        else:
            return HttpResponseRedirect('/products')
    else:
        return HttpResponseRedirect('/products')


# from django.db.models import F, Count,Max,Q,ExpressionWrapper, IntegerField

@login_required
def editProduct(request):
    product_id = request.POST.get('edit_product_id', '')
    new_product_name = request.POST.get('edit_product_name', '').capitalize()
    new_product_description = request.POST.get('edit_product_description', '')
    

    try:
        product_instance = get_object_or_404(Product, product_id=product_id, user=request.user)

        if product_instance.deleted_on is not None:
            existing_product = Product.objects.exclude(id=product_instance.id).filter(
                product_name=new_product_name,
                user=request.user,
                deleted_on__isnull=True
            )
        else:
            existing_product = Product.objects.exclude(id=product_instance.id).filter(
                product_name=new_product_name,
                user=request.user
            )

        if existing_product.exists():
            messages.info(request, 'Product with this name already exists!')
        else:
            # Check if there are changes
            if (
                new_product_name == product_instance.product_name and
                new_product_description == product_instance.product_description
            ):
                messages.info(request, 'No changes made to the product.')
            else:
                product_instance.product_name = new_product_name
                product_instance.product_description = new_product_description
                product_instance.updated_on = timezone.now()
                product_instance.save()
                messages.success(request, 'Product edited successfully!')

    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
    except Exception as e:
        print("test")
        messages.error(request, f'Failed editing product: {str(e)}')

    return HttpResponseRedirect('/products')

@transaction.atomic
@login_required
def delete_product(request, product_id):
    current_user = request.user

    if request.method == 'POST':
        order_quantity = Order.objects.filter(
            product_id=product_id,
            # status__in=['Ongoing', 'Pending'],
            deleted_on__isnull=True,
            user=current_user
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        inventory_quantity = InventoryDetails.objects.filter(
            product_id=product_id,
            user=current_user
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        if order_quantity > 0 or inventory_quantity > 0:
            messages.error(request, 'Products available in Order and Inventory')
            return JsonResponse({'status': 'error'})

        try:
            with transaction.atomic():
                product_instance = Product.objects.get(product_id=product_id, user=current_user)
                product_instance.deleted_on = timezone.now()  # Set the deleted_on field
                product_instance.save()
                messages.success(request, 'Product Deleted Successfully!')
                return JsonResponse({'status': 'success'})
        except Product.DoesNotExist:
            messages.error(request, 'Product not found!')
        except IntegrityError as e:
            messages.error(request, f'Failed marking product as deleted: {str(e)}')

    return render(request, 'products.html')


from datetime import datetime, timedelta


@login_required

def getOrder(request):
    current_user = request.user

    orders = Order.objects.filter(
        user_id=current_user,
        status__in=['Ongoing', 'Pending'],
        deleted_on__isnull=True
    ).select_related('product').order_by('-id')

    for order in orders:
        delivery_date = order.delivery_date
        current_date = timezone.now().date()

        if delivery_date < current_date:
            order.status = 'Pending'
            order.save()
        elif delivery_date == current_date or delivery_date > current_date:
            order.status = 'Ongoing'
            order.save()

    search_query = request.GET.get('q')

    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(ordered_date__icontains=search_query) |
            Q(delivery_date__icontains=search_query) |
            Q(completed_date__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)  # Search by product name (assuming it's a field in Product)
        )
    page = request.GET.get('page', 1)
    paginated_orders = paginate_data(orders, page, 20)
    context = {
        'orders': paginated_orders,
    }

    return render(request, 'orders.html', context)

@login_required

def getCompletedOrder(request):
    current_user_id = request.user.added_by

    # Retrieve completed orders using Django ORM
    completed_orders = Order.objects.filter(user_id=current_user_id, status='Completed', deleted_on__isnull=True).select_related('product').order_by('-id')
    
    search_query = request.GET.get('q')

    if search_query:
        completed_orders = completed_orders.filter(
            Q(order_id__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(ordered_date__icontains=search_query) |
            Q(delivery_date__icontains=search_query) |
            Q(completed_date__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)  # Search by product name (assuming it's a field in Product)
        )
    
    page = request.GET.get('page', 1)
    paginated_orders = paginate_data(completed_orders, page, 20)

    context = {
        'orders': paginated_orders,
    }

    return render(request, 'completedorder.html', context)

@login_required

def getCancelledOrder(request):
    current_user_id = request.user.added_by

    # Retrieve completed orders using Django ORM
    cancelled_orders = Order.objects.filter(user_id=current_user_id, status='Cancelled',deleted_on__isnull=True).select_related('product').order_by('-id')
    search_query = request.GET.get('q')

    if search_query:
        cancelled_orders = cancelled_orders.filter(
            Q(order_id__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(ordered_date__icontains=search_query) |
            Q(delivery_date__icontains=search_query) |
            Q(completed_date__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)

        )
    page = request.GET.get('page', 1)
    paginated_orders = paginate_data(cancelled_orders, page, 20)
    
    context = {
        'orders': paginated_orders,
    }
    

    return render(request, 'cancelledorder.html', context)

@login_required
def order_filter(request):
    if request.method == 'POST':
        basedon = request.POST.get('basedon')
        from_date = request.POST.get('from-date')
        to_date = request.POST.get('to-date')
        max_price = request.POST.get('max-price')
        min_price = request.POST.get('min-price')
        max_quantity = request.POST.get('max-quantity')
        min_quantity = request.POST.get('min-quantity')

        filter_params = {
            'user_id': request.user,
        }

        if from_date:
            filter_params[f'{basedon}__gte'] = from_date
        if to_date:
            filter_params[f'{basedon}__lte'] = to_date
        if min_price:
            filter_params['price__gte'] = min_price
        if max_price:
            filter_params['price__lte'] = max_price
        if min_quantity:
            filter_params['quantity__gte'] = min_quantity
        if max_quantity:
            filter_params['quantity__lte'] = max_quantity

        filtered_orders = Order.objects.filter(
            Q(user_id=request.user),
            **filter_params
        )

        context = {
           
            'orders':filtered_orders
        }
            # filteredList.append(context)

        return render(request, 'orders.html', context)

    return HttpResponseRedirect('/orders')

@login_required
def get_product_list(request):
    current_user_id = request.user.added_by
    sql_query_product = "SELECT id, product_name, product_id FROM product_info where user_id = %s AND deleted_on IS NULL"
    values = (current_user_id)
    product_list = []
    with connection.cursor() as cursor:
        cursor.execute(sql_query_product, values)
        products = cursor.fetchall()
        for product in products:
            product_list.append({'id': product[0], 'product': product[1], 'product_id': product[2]})
        
    return JsonResponse(product_list, safe=False)

def check_negative_values(fields):
    for field_name, value in fields.items():
        if value is not None and value < 0:
            raise ValueError(f"{field_name.capitalize()} cannot be less than 0.")


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
        product_name_object = Product.objects.get(product_id=order_product_name)
        product_name = product_name_object.product_name

        # Convert dates to datetime objects
        ordered_date = timezone.datetime.strptime(ordered_date, '%Y-%m-%d').date()
        delivery_date = timezone.datetime.strptime(delivery_date, '%Y-%m-%d').date()
        try:
            check_negative_values({
            'Quantity': Decimal(quantity),
            })
        except ValueError as ve:
            messages.error(request, str(ve))
            return render(request, 'orders.html')
        
        if delivery_date <= ordered_date:
            messages.error(request, 'Delivery date must be later than the order date.')
            return render(request, 'orders.html')

        # Fetch price from InventoryDetailsDate based on product_id and ordered_date
        try:
            inventory_entry = InventoryDetailsDate.objects.get(product__product_id=order_product_name,
                                                               date=ordered_date,
                                                               user=current_user_id)
            price = inventory_entry.price
            # Calculate total_price
            total_price = Decimal(quantity) * Decimal(price)
        except InventoryDetailsDate.DoesNotExist:
            # If price for the specified date is not found, get the latest price for the product
            latest_price_entry = InventoryDetailsDate.objects.filter(product__product_id=order_product_name,
                                                                      user=current_user_id).aggregate(Max('date'))
            latest_price_date = latest_price_entry['date__max']

            try:
                latest_inventory_entry = InventoryDetailsDate.objects.get(product__product_id=order_product_name,
                                                                           date=latest_price_date,
                                                                           user=current_user_id)
                price = latest_inventory_entry.price
                # Calculate total_price
                total_price = Decimal(quantity) * Decimal(price)
            except InventoryDetailsDate.DoesNotExist:
                messages.error(request, f'Price not found for the specified {product_name}.')
                price = 0
                total_price = 0

        # Insert order information into order_info table
        try:
            order=Order.objects.create(
                order_id=order_id,
                product=Product.objects.get(product_id=order_product_name),
                quantity=quantity,
                ordered_date=ordered_date,
                price=price,
                total_price=total_price,
                delivery_date=delivery_date,
                status=status,
                user_id=current_user_id
            )
            if status.lower() == 'completed':
                # If status is "completed", insert today's date into completed_date column
                order.completed_date = timezone.now().date()
                order.save()

            messages.success(request, 'New Order Added')

            previous_page = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(previous_page)
        except IntegrityError:
            return HttpResponse("An error occurred while adding the order")
        


    return render(request, 'orders.html')


@login_required

def editOrder(request):
    request.session['referring_page'] = request.META.get('HTTP_REFERER', '/')
    current_user_id = request.user.added_by

    if request.method == 'POST':
        old_order_id = request.POST.get('old_orderid', '')
        edit_quantity = request.POST.get('edit_quantity', '')
        edit_price = request.POST.get('edit_price', '')
        edit_delivery_date = request.POST.get('edit_delivery_date', '')
        edit_ordered_date = request.POST.get('edit_ordered_date', '')
        edit_status = request.POST.get('edit_status', '')

        try:
            check_negative_values({
                'Quantity': Decimal(edit_quantity),
                'Price': Decimal(edit_price)
            })
        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect(request.session['referring_page'])

        try:
            order = Order.objects.get(order_id=old_order_id, user_id=current_user_id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect(request.session['referring_page'])

        # Check if any changes have been made
        if (
            order.order_id == old_order_id and
            order.quantity == Decimal(edit_quantity) and
            order.price == Decimal(edit_price) and
            order.delivery_date == edit_delivery_date and
            order.ordered_date == edit_ordered_date and
            order.status == edit_status
        ):
            messages.info(request, f'No changes made to order {old_order_id}.')
            return redirect(request.session['referring_page'])

        # Check if the status is being changed to 'Completed'
        if edit_status == 'Completed':
            # Fetch the latest date for the product in InventoryDetailsDate
            latest_date = InventoryDetailsDate.objects.filter(
                product__product_id=order.product.product_id,
                user=current_user_id
            ).aggregate(latest_date=Max('date'))['latest_date']

            # Fetch the quantity for the latest date
            latest_quantity = InventoryDetailsDate.objects.filter(
                product__product_id=order.product.product_id,
                user=current_user_id,
                date=latest_date
            ).values('quantity').first()

            if latest_quantity is not None:
                latest_quantity = Decimal(latest_quantity['quantity'])
            else:
                latest_quantity = Decimal(0)

            if latest_quantity < Decimal(edit_quantity):
                messages.error(request, f"Cannot complete order {old_order_id}. Insufficient quantity in inventory.")
                return redirect(request.session['referring_page'])      

        # Update the order details
        order.quantity = Decimal(edit_quantity)
        order.price = Decimal(edit_price)
        order.total_price = Decimal(edit_quantity) * Decimal(edit_price)
        order.delivery_date = edit_delivery_date
        order.ordered_date = edit_ordered_date
        order.status = edit_status

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            try:
                if edit_status.lower() == 'completed':
                # If status is "completed", insert today's date into completed_date column
                    order.completed_date = timezone.now().date()
                order.save()
                order.save()
                messages.success(request, f'Order {old_order_id} Edited.')

                # If the order is completed, update InventoryDetailsDate
                if edit_status == 'Completed':
                    # Find the latest date for the product in InventoryDetailsDate
                    latest_date = InventoryDetailsDate.objects.filter(
                        product__product_id=order.product.product_id,
                        user=current_user_id
                    ).aggregate(Max('date'))['date__max']

                    # Deduct the quantity from the latest date
                    InventoryDetailsDate.objects.filter(
                        product__product_id=order.product.product_id,
                        user=current_user_id,
                        date=latest_date
                    ).update(
                        quantity_deducted=F('quantity_deducted') + Decimal(edit_quantity)
                    )

                    # Update the quantity by subtracting total quantity deducted
                    InventoryDetailsDate.objects.filter(
                        product__product_id=order.product.product_id,
                        user=current_user_id
                    ).update(
                        quantity=F('quantity') - F('quantity_deducted')
                    )

                return HttpResponseRedirect('/orders')
            except IntegrityError:
                return HttpResponse("An error occurred while editing the order details")

    return render(request, 'orders.html')


@login_required
def delete_order(request, order_id):
    current_user_id = request.user.added_by

    if request.method == 'POST':
        try:
            order = Order.objects.get(order_id=order_id, user_id=current_user_id)
            product_id = order.product.product_id
            
            order.deleted_on = datetime.now()
            order.save()
            
            # Get the referer from the request headers
            referer = request.META.get('HTTP_REFERER')

            return HttpResponseRedirect(referer or '/default-url/')

        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except IntegrityError as e:
            print(f"IntegrityError: {str(e)}")
            messages.error(request, "An error occurred while deleting the orders")

    return render(request, 'orders.html')

@login_required
def getProductCategory(request):
    category = request.GET.get('category')
    current_user_id =  request.user.added_by

    product_list = []
    with connection.cursor() as cursor:
        sql_query = "SELECT id, product_name, product_id FROM product_info WHERE userid =%s and deleted_on IS  NULL"
        cursor.execute(sql_query, [current_user_id])
        products = cursor.fetchall()
        # print(products)
        for product in products:
            product_list.append({'id': product[0], 'product': product[1], 'product_id': product[2]})

    return JsonResponse(product_list, safe=False)


from datetime import date

@login_required

def inventorylist(request, category_name):
    current_user_id = request.user

    # Retrieve the category instance
    category_instance = get_object_or_404(category, category=category_name, userid_id=current_user_id)

    # Retrieve the products for the category
    if category_instance:
        category_id = category_instance.id
    else:
        return render(request, 'inventoryhistory.html', {'items': [], 'product': []})

    # Retrieve products using Django ORM
    products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
    product_ids = [str(product['product_id']) for product in products]

    # Subquery to get the latest date for each product
    latest_dates_subquery = (
        InventoryDetailsDate.objects
        .filter(product_id=OuterRef('product_id'), user=current_user_id)
        .order_by('-date')
        .values('date')[:1]
    )

    # Retrieve the latest quantity for each product on the latest date
    inventory_details = (
        InventoryDetailsDate.objects
        .filter(product_id__in=product_ids, user=current_user_id)
        .annotate(latest_date=Subquery(latest_dates_subquery))
        .filter(date=F('latest_date'))
        .values('product_id', 'product__product_name', 'quantity')
    )

    items = []
    for row in inventory_details:
        item = {
            'quantity': row['quantity'],
            'product_id': row['product_id'],
            'product_name': row['product__product_name'],
        }
        items.append(item)

    page = request.GET.get('page', 1)
    paginated_items = paginate_data(items, page, 20)

    products_list = list(products)

    context = {
        'items': paginated_items,
        'product': products_list,
        'category_name': category_name
    } 
    return render(request, 'inventorylist.html', context)

@login_required

# def inventoryhistory(request, category_name):
#     current_user_id = request.user.id

#     # Retrieve category_id using Django ORM
#     category_info = category.objects.filter(category=category_name, userid_id=current_user_id).first()

#     if category_info:
#         category_id = category_info.id
#     else:
#         return render(request, 'inventoryhistory.html', {'items': [], 'product': []})

#     # Retrieve products using Django ORM
#     products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
#     product_ids = [str(product['product_id']) for product in products]

#     # Check if there are details for today's date for each product, otherwise add the required data
#     for product_id in product_ids:
#         today_details = InventoryDetailsDate.objects.filter(
#             product__product_id=product_id,
#             user_id=current_user_id,
#             date=date.today()
#         ).first()

#         if not today_details:
#             # If details for today's date do not exist, get the latest available details
#             latest_details = InventoryDetailsDate.objects.filter(
#                 product__product_id=product_id,
#                 user_id=current_user_id
#             ).order_by('-date').first()

#             if latest_details:
#                 # If there are details available, create data for today using the latest available details
#                 InventoryDetailsDate.objects.create(
#                     user_id=current_user_id,
#                     product_id=product_id,
#                     quantity=latest_details.quantity,
#                     quantity_added=0,
#                     quantity_deducted=0,
#                     price=latest_details.price,
#                     date=date.today()
#                 )
#             else:
#                 # If no details are available, create data with default values
#                 InventoryDetailsDate.objects.create(
#                     user_id=current_user_id,
#                     product_id=product_id,
#                     quantity=0,
#                     quantity_added=0,
#                     quantity_deducted=0,
#                     price=0,
#                     date=date.today()
#                 )

#     # Retrieve products and inventory details after adding the required data
#     products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
#     product_ids = [str(product['product_id']) for product in products]

#     inventory_details = InventoryDetailsDate.objects.filter(
#         product__product_id__in=product_ids,
#         user_id=current_user_id
#     ).order_by('-id')

#     # Convert Django ORM QuerySet to list of dictionaries
#     products_list = list(products)
#     inventory_list = list(inventory_details)
#     page = request.GET.get('page', 1)
#     paginated_items = paginate_data(inventory_list, page, 20)

#     context = {
#         'items': paginated_items,
#         'product': products_list
#     }
#     return render(request, 'inventoryhistory.html', context)

def inventoryhistory(request, category_name):
    current_user_id = request.user.id

    # Retrieve category_id using Django ORM
    category_info = category.objects.filter(category=category_name, userid_id=current_user_id).first()

    if category_info:
        category_id = category_info.id
    else:
        return render(request, 'inventoryhistory.html', {'items': [], 'product': []})
    category_name = category_info.category

    # Retrieve products using Django ORM
    products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
    product_ids = [str(product['product_id']) for product in products]

    # Define the search query
    search_query = request.GET.get('q')

    # Define the date filter
    date_filter = request.GET.get('date')

    # Define the quantity_added filter
    quantity_added_filter = request.GET.get('quantity_added')

    # Define the quantity_deducted filter
    quantity_deducted_filter = request.GET.get('quantity_deducted')

    # Define the quantity filter
    quantity_filter = request.GET.get('quantity')

    # Filter products based on the search query if available
    if search_query:
        products = products.filter(product_name__icontains=search_query)
        product_ids = [str(product['product_id']) for product in products]

    # Check if there are details for today's date for each product, otherwise add the required data
    for product_id in product_ids:
        today_details = InventoryDetailsDate.objects.filter(
            product__product_id=product_id,
            user_id=current_user_id,
            date=date.today()
        ).first()

        if not today_details:
            # If details for today's date do not exist, get the latest available details
            latest_details = InventoryDetailsDate.objects.filter(
                product__product_id=product_id,
                user_id=current_user_id
            ).order_by('-date').first()

            if latest_details:
                # If there are details available, create data for today using the latest available details
                InventoryDetailsDate.objects.create(
                    user_id=current_user_id,
                    product_id=product_id,
                    quantity=latest_details.quantity,
                    quantity_added=0,
                    quantity_deducted=0,
                    price=latest_details.price,
                    date=date.today()
                )
            else:
                # If no details are available, create data with default values
                InventoryDetailsDate.objects.create(
                    user_id=current_user_id,
                    product_id=product_id,
                    quantity=0,
                    quantity_added=0,
                    quantity_deducted=0,
                    price=0,
                    date=date.today()
                )

    # Retrieve products and inventory details after adding the required data
    products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
    product_ids = [str(product['product_id']) for product in products]

    inventory_details = InventoryDetailsDate.objects.filter(
        product__product_id__in=product_ids,
        user_id=current_user_id
    ).order_by('-id')

    # Filter inventory details based on the search query and other filters if available
    if search_query:
        inventory_details = inventory_details.filter(
            Q(product__product_name__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(quantity_added__icontains=search_query) |
            Q(quantity_deducted__icontains=search_query) |
            Q(price__icontains=search_query)
        )

    if date_filter:
        inventory_details = inventory_details.filter(date=date_filter)

    if quantity_added_filter:
        inventory_details = inventory_details.filter(quantity_added=quantity_added_filter)

    if quantity_deducted_filter:
        inventory_details = inventory_details.filter(quantity_deducted=quantity_deducted_filter)

    if quantity_filter:
        inventory_details = inventory_details.filter(quantity=quantity_filter)

    # Convert Django ORM QuerySet to list of dictionaries
    products_list = list(products)
    inventory_list = list(inventory_details)
    page = request.GET.get('page', 1)
    paginated_items = paginate_data(inventory_list, page, 20)

    context = {
        'items': paginated_items,
        'product': products_list,
        'category_name':category_name
    }
    return render(request, 'inventoryhistory.html', context)

@login_required

def addItems(request):
    request.session['referring_page'] = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        product = request.POST.get('getProductCategory', '')
        quantity = request.POST.get('quantity', '')
        price = request.POST.get('price', '')
        current_user_id = request.user.added_by
        current_date = timezone.now().date()

        try:
            check_negative_values({
            'Quantity': Decimal(quantity),
            'Price': Decimal(price)
            })
        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect(request.session['referring_page'])


        try:
            # Try to get existing entry in InventoryDetailsDate
            existing_data_history = InventoryDetailsDate.objects.get(product_id=product, date=current_date, user_id=current_user_id)
            existing_data_history.quantity_added = str(int(existing_data_history.quantity_added) + int(quantity))
                                                
            existing_data_history.quantity = str(int(existing_data_history.quantity) + int(quantity))
            existing_data_history.price = price  # You can modify this if needed
            existing_data_history.save()
            messages.success(request, "Inventory Updated")

        except InventoryDetailsDate.DoesNotExist:
            # If no entry exists, insert a new row into inventorydetails_date
            new_entry_history = InventoryDetailsDate(product_id=product, quantity=quantity, quantity_added = quantity, quantity_deducted='0', price=price, user_id=current_user_id, date=current_date)
            new_entry_history.save()
            messages.success(request, "Inventory Added")

        except IntegrityError as e:
            # Handle the IntegrityError, log it, or display an error message
            messages.error(request, f"IntegrityError: {str(e)}")
            return redirect(request.session['referring_page'])

        try:
            # Try to get existing entry in Order
            existing_data_order_info = Order.objects.filter(product_id=product, ordered_date=current_date, user_id=current_user_id)
            if existing_data_order_info.exists():
                for order_info in existing_data_order_info:
                    order_info.price = price if price else order_info.price
                    order_info.save()

                    order_info.total_price = str(int(order_info.quantity) * int(order_info.price))
                    order_info.save()

                messages.success(request, "Orders Updated")
            else:
                messages.warning(request, "No orders for the current date and conditions")

        except IntegrityError as e:
            messages.error(request, f"IntegrityError: {str(e)}")
            return redirect(request.session['referring_page'])
            

    return redirect(request.session['referring_page'])

@login_required

def editItems(request):
    if request.method == 'POST':
        request.session['referring_page'] = request.META.get('HTTP_REFERER', '/')
        inventory_id = request.POST.get('edit_inventory_id', '')
        quantity_added = request.POST.get('edit_quantity_added', '')
        quantity_deducted = request.POST.get('edit_quantity_deducted', '')
        price = request.POST.get('edit_price_inventory', '')
        operation = request.POST.get('edit_operation', '')
        current_user_id = request.user.added_by
        print("test", price)
    
        try:
            # Convert quantity_added and quantity_deducted to integers
            if quantity_added != "":
                quantity_added = int(quantity_added)
            if quantity_deducted != "":
                quantity_deducted = int(quantity_deducted)
        except ValueError:
            messages.error(request, "Invalid quantity value")
            return redirect(request.session['referring_page'])
        
        try:
            check_negative_values({
                'Quantity Added': Decimal(quantity_added) if quantity_added != "" else 0,
                'Quantity Deducted': Decimal(quantity_deducted) if quantity_deducted != "" else 0
            })
        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect(request.session['referring_page'])

        try:
            existing_data_history = InventoryDetailsDate.objects.get(id=inventory_id, user_id=current_user_id)
            existing_quantity_added = int(existing_data_history.quantity_added)
            existing_quantity_deducted = int(existing_data_history.quantity_deducted)
            existing_data_quantity = int(existing_data_history.quantity)
            date = existing_data_history.date

            if quantity_added != "":
                new_quantity_added = existing_quantity_added + quantity_added
            else:
                new_quantity_added = existing_quantity_added
                quantity_added = 0

            # if quantity_deducted != "":
            #     new_quantity_deducted = existing_quantity_deducted + quantity_deducted
            # else:
            #     new_quantity_deducted = existing_quantity_deducted
            #     quantity_deducted = 0
                
            if quantity_deducted != "":
                new_quantity_deducted = quantity_deducted
            else:
                new_quantity_deducted = 0
                quantity_deducted = 0

            if new_quantity_deducted > existing_data_quantity:
                messages.error(request, "Deducted quantity cannot be greater than available quantity")
                return redirect(request.session['referring_page'])

            # Check if there are no changes in quantity added, quantity deducted, and price
            # if new_quantity_added == existing_quantity_added and new_quantity_deducted == existing_quantity_deducted and price == existing_data_history.price:
            #     messages.info(request, "No changes in quantity added, quantity deducted, and price.")
            #     return redirect(request.session['referring_page'])
            else:
                # Update inventory details based on changes
                with transaction.atomic():
                    existing_data_history.quantity_added = new_quantity_added
                    existing_data_history.quantity_deducted = existing_quantity_deducted+new_quantity_deducted
                    existing_data_history.quantity = int(existing_data_history.quantity)+int(quantity_added) - int(quantity_deducted)
                    existing_data_history.price = price if price != "" else existing_data_history.price
                    existing_data_history.save()

                    # Deduct or add quantity for later dates
                    later_dates = InventoryDetailsDate.objects.filter(
                        product__product_id=existing_data_history.product_id,
                        user_id=current_user_id,
                        date__gt=date
                    )

                   
                    

                    for later_date in later_dates:
                        print(later_date.date)
                        if quantity_added:
                            quantity_added_value = int(quantity_added)
                        else:
                            quantity_added_value = 0

                        if quantity_deducted:
                            quantity_deducted_value = int(quantity_deducted)
                        else:
                            quantity_deducted_value = 0

                        later_date.quantity = str(int(later_date.quantity) + quantity_added_value - quantity_deducted_value)
                        later_date.save()
                    

                product = existing_data_history.product_id
                messages.success(request, "Inventory Updated")
                print("Product", product)
            
            try:
                existing_data_order_info = Order.objects.filter(product_id=product, ordered_date=date, user_id=current_user_id,deleted_on__isnull=True)
                if existing_data_order_info.exists():
                    for order_info in existing_data_order_info:
                        order_info.price = price if price else order_info.price
                        order_info.save()

                        order_info.total_price = str(int(order_info.quantity) * int(order_info.price))
                        order_info.save()

                    messages.success(request, "Orders Updated")
                else:
                    messages.warning(request, "No orders for the current date and conditions")

            except IntegrityError as e:
                messages.error(request, f"IntegrityError: {str(e)}")
                return redirect(request.session['referring_page'])

        except InventoryDetailsDate.DoesNotExist:
            messages.error(request, "Inventory does not exist for editing")

        return redirect(request.session['referring_page'])

    return render(request, 'inventoryhistory.html')
# def editItems(request):
#     if request.method == 'POST':
#         request.session['referring_page'] = request.META.get('HTTP_REFERER', '/')
#         inventory_id = request.POST.get('edit_inventory_id', '')
#         quantity_added = request.POST.get('edit_quantity_added', '')
#         quantity_deducted = request.POST.get('edit_quantity_deducted', '')
#         price = request.POST.get('edit_price_inventory', '')
#         operation = request.POST.get('edit_operation', '')
#         current_user_id = request.user.added_by
#         print("test", price)
    
#         try:
#             # Convert quantity_added and quantity_deducted to integers
#             if quantity_added != "":
#                 quantity_added = int(quantity_added)
#             if quantity_deducted != "":
#                 quantity_deducted = int(quantity_deducted)
#         except ValueError:
#             messages.error(request, "Invalid quantity value")
#             return redirect(request.session['referring_page'])
        
#         try:
#             check_negative_values({
#                 'Quantity Added': Decimal(quantity_added) if quantity_added != "" else 0,
#                 'Quantity Deducted': Decimal(quantity_deducted) if quantity_deducted != "" else 0
#             })
#         except ValueError as ve:
#             messages.error(request, str(ve))
#             return redirect(request.session['referring_page'])

#         try:
#             existing_data_history = InventoryDetailsDate.objects.get(id=inventory_id, user_id=current_user_id)
#             existing_quantity_added = int(existing_data_history.quantity_added)
#             existing_quantity_deducted = int(existing_data_history.quantity_deducted)
#             date = existing_data_history.date

#             if quantity_added != "":
#                 new_quantity_added = existing_quantity_added + quantity_added
#             else:
#                 new_quantity_added = existing_quantity_added

#             if quantity_deducted != "":
#                 new_quantity_deducted = existing_quantity_deducted + quantity_deducted
#             else:
#                 new_quantity_deducted = existing_quantity_deducted

#             if new_quantity_deducted > existing_quantity_added:
#                 messages.error(request, "Deducted quantity cannot be greater than available quantity")
#                 return redirect(request.session['referring_page'])

#             # Check if there are no changes in quantity added, quantity deducted, and price
#             if new_quantity_added == existing_quantity_added and new_quantity_deducted == existing_quantity_deducted and price == existing_data_history.price:
#                 messages.info(request, "No changes in quantity added, quantity deducted, and price.")
#                 return redirect(request.session['referring_page'])
#             else:

#                 # Update inventory details based on changes
#                 existing_data_history.quantity_added = new_quantity_added
#                 existing_data_history.quantity_deducted = new_quantity_deducted
#                 existing_data_history.quantity = new_quantity_added - new_quantity_deducted
#                 existing_data_history.price = price if price != "" else existing_data_history.price
#                 existing_data_history.save()

#                 product = existing_data_history.product_id
#                 messages.success(request, "Inventory Updated")
#                 print("Product", product)
            
#             try:
#                 existing_data_order_info = Order.objects.filter(product_id=product, ordered_date=date, user_id=current_user_id)
#                 if existing_data_order_info.exists():
#                     for order_info in existing_data_order_info:
#                         order_info.price = price if price else order_info.price
#                         order_info.save()

#                         order_info.total_price = str(int(order_info.quantity) * int(order_info.price))
#                         order_info.save()

#                     messages.success(request, "Orders Updated")
#                 else:
#                     messages.warning(request, "No orders for the current date and conditions")

#             except IntegrityError as e:
#                 messages.error(request, f"IntegrityError: {str(e)}")
#                 return redirect(request.session['referring_page'])

#         except InventoryDetailsDate.DoesNotExist:
#             messages.error(request, "Inventory does not exist for editing")

#         return redirect(request.session['referring_page'])

#     return render(request, 'inventoryhistory.html')

# def editItems(request):
#     if request.method == 'POST':
#         request.session['referring_page'] = request.META.get('HTTP_REFERER', '/')
#         inventory_id = request.POST.get('edit_inventory_id', '')
#         # product = request.POST.get('product_dropdown', '')
#         quantity_added = request.POST.get('edit_quantity_added', '')
#         quantity_deducted = request.POST.get('edit_quantity_deducted', '')
#         price = request.POST.get('edit_price_inventory', '')
#         operation = request.POST.get('edit_operation', '')
#         current_user_id = request.user.added_by
#         print("test",price)
    
#         try:
#             # Convert quantity_added and quantity_deducted to integers
#             quantity_added = int(quantity_added)
#             quantity_deducted = int(quantity_deducted)
#         except ValueError:
#             messages.error(request, "Invalid quantity value")
#             # return redirect(request.path)  # Redirect to the same page
#             return redirect(request.session['referring_page'])
        
#         try:
#             check_negative_values({
#             'Quantity Added': Decimal(quantity_added),
#             'Quantity Deducted': Decimal(quantity_deducted)
#             })
#         except ValueError as ve:
#             messages.error(request, str(ve))
#             return redirect(request.session['referring_page'])

#         try:
#             existing_data_history = InventoryDetailsDate.objects.get(id=inventory_id, user_id=current_user_id)
#             existing_quantity_added = int(existing_data_history.quantity_added)
#             existing_quantity_deducted = int(existing_data_history.quantity_deducted)
#             date = existing_data_history.date

#             new_quantity_added = existing_quantity_added + quantity_added
#             new_quantity_deducted = existing_quantity_deducted + quantity_deducted

#             if new_quantity_deducted > existing_quantity_added:
#                 messages.error(request, "Deducted quantity cannot be greater than available quantity")
#                 return redirect(request.session['referring_page'])

#             # Update inventory details based on changes
#             existing_data_history.quantity_added = new_quantity_added
#             existing_data_history.quantity_deducted = new_quantity_deducted
#             existing_data_history.quantity = new_quantity_added - new_quantity_deducted
#             exisiting_price = existing_data_history.price 
#             print(exisiting_price)
#             if price != "":
#                 existing_data_history.price = price
            

#             existing_data_history.save()

#             product=existing_data_history.product_id 
#             existing_data_history.save()    
#             print("Product", product)
#             try:
#                 existing_data_order_info = Order.objects.filter(product_id=product, ordered_date=date, user_id=current_user_id)
#                 if existing_data_order_info.exists():
#                     for order_info in existing_data_order_info:
#                         order_info.price = price if price else order_info.price
#                         order_info.save()

#                         order_info.total_price = str(int(order_info.quantity) * int(order_info.price))
#                         order_info.save()

#                     messages.success(request, "Orders Updated")
#                 else:
#                     messages.warning(request, "No orders for the current date and conditions")

#             except IntegrityError as e:
#                 messages.error(request, f"IntegrityError: {str(e)}")
#                 return redirect(request.session['referring_page'])

#         except InventoryDetailsDate.DoesNotExist:
#             messages.error(request, "Inventory does not exist for editing")

#         return redirect(request.session['referring_page'])

#     return render(request, 'inventoryhistory.html')

@login_required
def getItems(request):
    current_user_id = request.user.added_by
    sql_query_inventory = "SELECT * FROM inventory_details where user_id = %d"
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

@login_required


def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for maintaining the user's session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('changepassword')  # Redirect to the same page after successful password change
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'changepassword.html', {'form': form})

# def arima_sarimax_forecast(data, forecast_steps=12):
#     # Convert 'Month' column to datetime format if not already
#     data['Month'] = pd.to_datetime(data['Month'])

#     # Set 'Month' as the index
#     data.set_index('Month', inplace=True)

#     # Perform differencing to make the time series stationary
#     data_diff = data['Sales'].diff().dropna()

#     # Use pmdarima to automatically choose the best parameters for ARIMA
#     arima_model = pm.auto_arima(data['Sales'], seasonal=False, suppress_warnings=True, stepwise=True)
#     arima_order = arima_model.get_params()['order']

#     # Fit ARIMA model
#     arima_result = ARIMA(data['Sales'], order=arima_order).fit()

#     # Use pmdarima to automatically choose the best parameters for SARIMAX
#     sarimax_model = pm.auto_arima(data['Sales'], seasonal=True, suppress_warnings=True, stepwise=True, m=12)
#     sarimax_order = sarimax_model.get_params()['order']
#     sarimax_seasonal_order = sarimax_model.get_params()['seasonal_order']

#     # Fit SARIMAX model
#     sarimax_result = sm.tsa.statespace.SARIMAX(data['Sales'], order=sarimax_order, seasonal_order=sarimax_seasonal_order).fit()

#     # Forecast using ARIMA
#     # arima_forecast_steps = 12
#     arima_forecast = arima_result.get_forecast(steps=forecast_steps)
#     arima_confidence_intervals = arima_forecast.conf_int()

#     # Forecast using SARIMAX
#     # sarimax_forecast_steps = 12
#     sarimax_forecast = sarimax_result.get_forecast(steps=forecast_steps)
#     sarimax_confidence_intervals = sarimax_forecast.conf_int()

#     return {
#         'arima_forecast': arima_forecast.predicted_mean,
#         'arima_confidence_intervals': arima_confidence_intervals,
#         'sarimax_forecast': sarimax_forecast.predicted_mean,
#         'sarimax_confidence_intervals': sarimax_confidence_intervals,
#     }

from datetime import datetime

def arima_sarimax_forecast(data):
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

    # Get the current date
    current_date = datetime.now()

    # Forecast for the next 12 months from the current month
    forecast_steps = 12 - current_date.month + 1  # Adjusting for the current month

    # Forecast using ARIMA
    arima_forecast = arima_result.get_forecast(steps=forecast_steps)
    arima_confidence_intervals = arima_forecast.conf_int()

    # Forecast using SARIMAX
    sarimax_forecast = sarimax_result.get_forecast(steps=forecast_steps)
    sarimax_confidence_intervals = sarimax_forecast.conf_int()

    return {
        'arima_forecast': arima_forecast.predicted_mean,
        'arima_confidence_intervals': arima_confidence_intervals,
        'sarimax_forecast': sarimax_forecast.predicted_mean,
        'sarimax_confidence_intervals': sarimax_confidence_intervals,
    }