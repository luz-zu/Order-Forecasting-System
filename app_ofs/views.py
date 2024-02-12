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
from django.template.defaultfilters import date as django_date_filter


from django.db.models import Sum ,F, Count,Max,Q,ExpressionWrapper, IntegerField,Subquery, OuterRef,Q

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import JsonResponse
from django.db import IntegrityError
from .models import category, Product, InventoryDetails, InventoryDetailsDate, Order,CustomUser,ForecastData,ProductStatistics  
from .forms import CategoryForm
from django.contrib.auth.decorators import login_required
from django.core.management.base import BaseCommand
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
        user = authenticate(request, username=username, password=password, deleted_on__isnull=True)
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
                # form.instance.company_id = 1
                # Check if there are existing records
                if CustomUser.objects.exists():
                    # Get the latest company_id and increment by 1
                    latest_company_id = CustomUser.objects.latest('company_id').company_id
                    form.instance.company_id = latest_company_id + 1
                else:
                    # Start with company_id = 1
                    form.instance.company_id = 1
                form.save()
                messages.success(request, 'Registration successful! You are now logged in.')
                return HttpResponseRedirect('/register')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def forecast(request):
    current_user_id = request.user.company_id

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
# def user_dashboard(request):
#     # Fetch the last 12 months and future 12 months forecast data if available
#     current_date = datetime.now().date()
#     # current_date = datetime(2024, 5, 1).date()
#     current_month = current_date.replace(day=1)
#     last_12_months = current_date - relativedelta(months=12)
#     next_12_months = current_date + relativedelta(months=12)
    
#     # Check if there's any missing data in the next 12 months (excluding the current month)
#     missing_data_exists = any(not ForecastData.objects.filter(ordered_date=current_month + relativedelta(months=i)).exists() for i in range(1, 13) if current_month + relativedelta(months=i) != current_month)

#     if missing_data_exists:
#         # Perform ARIMA or SARIMAX forecast if data doesn't exist in the given range
#         data_queryset = ForecastData.objects.all().values('ordered_date', 'quantity')
#         data = pd.DataFrame(data_queryset)
#         data.columns = ["Month", "Sales"]
#         data = data.dropna()

#         results = arima_sarimax_forecast(data)
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

#             # Do not update data for current month
#             if existing_data.exists() and date.month != current_date.month:
#                 # Update existing data
#                 existing_data.update(
#                     forecasted_quantity=forecast_value,
#                     lower_ci_sarimax=lower_ci,
#                     upper_ci_sarimax=upper_ci
#                 )
#             elif not existing_data.exists():
#                 # Create new data
#                 ForecastData.objects.create(
#                     quantity=0,
#                     ordered_date=date,
#                     forecasted_quantity=forecast_value,
#                     lower_ci_sarimax=lower_ci,
#                     upper_ci_sarimax=upper_ci
#                 )

#     # Fetch updated forecast data queryset after potential updates
#     forecast_data_queryset = ForecastData.objects.filter(ordered_date__gte=last_12_months, ordered_date__lte=next_12_months).order_by('ordered_date')
#     actual_data = ForecastData.objects.filter(ordered_date__lt=current_date - relativedelta(months=1), ordered_date__gte=last_12_months).order_by('ordered_date')

#     actual_quantity = [actual.quantity for actual in actual_data]

#     forecast_dates = [forecast.ordered_date.strftime("%b %Y") for forecast in forecast_data_queryset]
#     forecast_quantity = [forecast.forecasted_quantity for forecast in forecast_data_queryset]
#     upper_ci_sarimax = [forecast.upper_ci_sarimax for forecast in forecast_data_queryset]
#     lower_ci_sarimax = [forecast.lower_ci_sarimax for forecast in forecast_data_queryset]

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


def user_dashboard(request):
    # Fetch the last 12 months and future 30 days forecast data if available
    user = request.user.added_by
    total_orders = Order.objects.filter(user=user,deleted_on__isnull=True).count()
    pending_orders = Order.objects.filter(user=user, status='Pending',deleted_on__isnull=True).count()
    ongoing_orders = Order.objects.filter(user=user, status='Ongoing',deleted_on__isnull=True).count()
    completed_orders = Order.objects.filter(user=user, status='Completed',deleted_on__isnull=True).count()


    
    current_date = datetime.now().date()
    current_month = current_date.replace(day=1)
    next_30_days = current_date + timedelta(days=30)

    last_7_days = current_date - timedelta(days=7)
    orders_per_day_last_7_days = Order.objects.filter(user=user, ordered_date__gte=last_7_days, ordered_date__lte=current_date).values('ordered_date').annotate(num_orders=Count('id')).order_by('ordered_date')

    # Extract dates and corresponding number of orders
    order_dates = [order['ordered_date'].strftime("%b %d, %Y") for order in orders_per_day_last_7_days]
    num_orders_per_day = [order['num_orders'] for order in orders_per_day_last_7_days]

    # Create a bar graph of orders per day for the last 7 days
    bar_graph = go.Figure(data=[go.Bar(x=order_dates, y=num_orders_per_day)])
    bar_graph.update_layout(title='Number of Orders per Day for Last 7 Days', xaxis_title='Date', yaxis_title='Number of Orders')

    # Convert bar graph to HTML
    bar_graph_html = bar_graph.to_html(full_html=False)
    
    # Check if there's any missing data in the next 30 days (excluding the current day)
    missing_data_exists = any(not ForecastData.objects.filter(ordered_date=current_date + timedelta(days=i)).exists() for i in range(1, 31) if current_date + timedelta(days=i) != current_date)

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

            # Do not update data for current date
            if existing_data.exists() and date != current_date:
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
    forecast_data_queryset = ForecastData.objects.filter(ordered_date__gte=current_date, ordered_date__lte=next_30_days).order_by('ordered_date')
    actual_data = ForecastData.objects.filter(ordered_date__lt=current_date, ordered_date__gte=current_date - relativedelta(months=1)).order_by('ordered_date')

    actual_quantity = [actual.quantity for actual in actual_data]

    forecast_dates = [forecast.ordered_date.strftime("%b %d, %Y") for forecast in forecast_data_queryset]
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
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'ongoing_orders': ongoing_orders,
        'completed_orders': completed_orders,
        'orders_per_day_last_7_days': orders_per_day_last_7_days,
        'bar_graph_html': bar_graph_html,
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
    current_user = request.user.added_by

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
def get_products(request):
    if request.method == 'GET' and request.is_ajax():
        category_id = request.GET.get('category') or request.GET.get('categorySelect_order_filter')
        if category_id:
            products = Product.objects.filter(category_id=category_id)
            product_data = [{'product_id': product.product_id, 'product_name': product.product_name} for product in products]
            return JsonResponse(product_data, safe=False)
    return JsonResponse([], safe=False)


from django.db.models import Sum, Avg
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractWeek,ExtractYear
from datetime import date, timedelta

def daily_statistics(product_id, from_date=None, to_date=None, selected_columns=None):
    # Query database to get the data
    daily_stats = ProductStatistics.objects.filter(product_id=product_id, date__gte=from_date, date__lte=to_date).order_by('date')
    
    daily_stats_data = []

    dates = [entry.date.strftime("%b %d, %Y") for entry in daily_stats]
    for entry in daily_stats:
        date = entry.date
        order_quantity = entry.order_quantity
        completed_quantity = entry.completed_quantity
        production_quantity = entry.production_quantity
        cancelled_quantity = entry.cancelled_quantity
        
        daily_data = {
            'date': date,
            'order_quantity': order_quantity,
            'completed_quantity': completed_quantity,
            'production_quantity': production_quantity,
            'cancelled_quantity': cancelled_quantity
        }
        
        # Append the dictionary to the list
        daily_stats_data.append(daily_data)

    traces = []

    # Add traces for selected columns
    if selected_columns is None or 'order_quantity' in selected_columns:
        order_quantity = [int(entry.order_quantity) for entry in daily_stats]
        trace_order_quantity = go.Scatter(x=dates, y=order_quantity, mode='lines', name='Order Quantity')
        traces.append(trace_order_quantity)
    
    if selected_columns is None or 'completed_quantity' in selected_columns:
        completed_quantity = [int(entry.completed_quantity) for entry in daily_stats]
        trace_completed_quantity = go.Scatter(x=dates, y=completed_quantity, mode='lines', name='Completed Quantity')
        traces.append(trace_completed_quantity)
    
    if selected_columns is None or 'cancelled_quantity' in selected_columns:
        cancelled_quantity = [int(entry.cancelled_quantity) for entry in daily_stats]
        trace_cancelled_quantity = go.Scatter(x=dates, y=cancelled_quantity, mode='lines', name='Cancelled Quantity')
        traces.append(trace_cancelled_quantity)
    
    if selected_columns is None or 'production_quantity' in selected_columns:
        production_quantity = [int(entry.production_quantity) for entry in daily_stats]
        trace_production_quantity = go.Scatter(x=dates, y=production_quantity, mode='lines', name='Production Quantity')
        traces.append(trace_production_quantity)

    # Create a Plotly figure
    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(title='Daily Statistics',
                      xaxis=dict(title='Date', tickangle=90),
                      yaxis=dict(title='Quantity'),
                      xaxis_rangeslider_visible=True,autosize=True)  # Enable scrollbar

    # Convert figure to HTML
    plot_div = fig.to_html(full_html=False)


    return daily_stats_data, plot_div


import calendar
from calendar import monthrange
from django.db.models.functions import Cast

def monthly_statistics(product_id, from_date=None, to_date=None, selected_columns=None):
    monthly_stats = ProductStatistics.objects.filter(product_id=product_id, date__gte=from_date, date__lte=to_date).order_by('date')

    monthly_stats = monthly_stats.annotate(
        month=ExtractMonth('date'),
        year=ExtractYear('date')
    ).values('month', 'year').annotate(
        total_order_quantity=Cast(Sum('order_quantity'), IntegerField()),
        total_completed_quantity=Cast(Sum('completed_quantity'), IntegerField()),
        total_production_quantity=Cast(Sum('production_quantity'), IntegerField()),
        total_cancelled_quantity=Cast(Sum('cancelled_quantity'), IntegerField()),
        average_order_quantity=Cast(Avg('order_quantity'), IntegerField()),
        average_completed_quantity=Cast(Avg('completed_quantity'), IntegerField()),
        average_production_quantity=Cast(Avg('production_quantity'), IntegerField()),
        average_cancelled_quantity=Cast(Avg('cancelled_quantity'), IntegerField())
    ).order_by('year', 'month')

    # Calculate start and end dates for each month
    for entry in monthly_stats:
        year = entry['year']
        month = entry['month']
        days_in_month = monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, days_in_month)
        entry['start_date'] = start_date
        entry['end_date'] = end_date


    x_labels = [calendar.month_name[entry['month']] + ' ' + str(entry['year']) for entry in monthly_stats]

    traces = []
    if selected_columns is None or 'order_quantity' in selected_columns:
        total_order_quantity = [entry['total_order_quantity'] for entry in monthly_stats]
        trace_total_order_quantity = go.Bar(x=x_labels, y=total_order_quantity, name='Total Order Quantity')
        traces.append(trace_total_order_quantity)
    
    if selected_columns is None or 'completed_quantity' in selected_columns:
        total_completed_quantity = [entry['total_completed_quantity'] for entry in monthly_stats]
        trace_total_completed_quantity = go.Bar(x=x_labels, y=total_completed_quantity, name='Total Completed Quantity')
        traces.append(trace_total_completed_quantity)
    
    if selected_columns is None or 'cancelled_quantity' in selected_columns:
        total_cancelled_quantity = [entry['total_cancelled_quantity'] for entry in monthly_stats]
        trace_total_cancelled_quantity = go.Bar(x=x_labels, y=total_cancelled_quantity, name='Total Cancelled Quantity')
        traces.append(trace_total_cancelled_quantity)
    
    if selected_columns is None or 'production_quantity' in selected_columns:
        total_production_quantity = [entry['total_production_quantity'] for entry in monthly_stats]
        trace_total_production_quantity = go.Bar(x=x_labels, y=total_production_quantity, name='Total Production Quantity')
        traces.append(trace_total_production_quantity)

        
    if selected_columns is None or 'order_quantity' in selected_columns:
        average_order_quantity = [entry['average_order_quantity'] for entry in monthly_stats]
        trace_average_order_quantity = go.Bar(x=x_labels, y=average_order_quantity, name='Average Order Quantity')
        traces.append(trace_average_order_quantity)
    
    if selected_columns is None or 'completed_quantity' in selected_columns:
        average_completed_quantity = [entry['average_completed_quantity'] for entry in monthly_stats]
        trace_average_completed_quantity = go.Bar(x=x_labels, y=average_completed_quantity, name='Average Completed Quantity')
        traces.append(trace_average_completed_quantity)
    
    if selected_columns is None or 'cancelled_quantity' in selected_columns:
        average_cancelled_quantity = [entry['average_cancelled_quantity'] for entry in monthly_stats]
        trace_average_cancelled_quantity = go.Bar(x=x_labels, y=average_cancelled_quantity, name='Average Cancelled Quantity')
        traces.append(trace_average_cancelled_quantity)
    
    if selected_columns is None or 'production_quantity' in selected_columns:
        average_production_quantity = [entry['average_production_quantity'] for entry in monthly_stats]
        trace_average_production_quantity = go.Bar(x=x_labels, y=average_production_quantity, name='Average Production Quantity')
        traces.append(trace_average_production_quantity)

    


    # Create a Plotly figure
    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(title='Monthly Statistics',
                      xaxis=dict(title='Month and Year'),
                      yaxis=dict(title='Quantity'),
                      xaxis_rangeslider_visible=True)

    # Convert figure to HTML
    plot_div = fig.to_html(full_html=False)

    return plot_div, monthly_stats,selected_columns


from django.db.models import Min, Max

# def weekly_statistics(product_id, from_date=None, to_date=None, selected_columns=None):
#     # Filter the queryset by product_id and date range
#     weekly_stats = ProductStatistics.objects.filter(product_id=product_id).order_by('date')
#     if from_date and to_date:
#         weekly_stats = weekly_stats.filter(date__range=[from_date, to_date])
    

#     # Annotate the queryset to calculate week number, start date, and end date
#     weekly_stats = weekly_stats.annotate(
#         week=ExtractWeek('date'),
#         start_date=Min('date'),
#         end_date=Max('date')
#     ).values('week', 'start_date', 'end_date').annotate(
#         total_order_quantity=Sum('order_quantity'),
#         total_completed_quantity=Sum('completed_quantity'),
#         total_production_quantity=Sum('production_quantity'),
#         total_cancelled_quantity=Sum('cancelled_quantity'),
#         average_order_quantity=Avg('order_quantity'),
#         average_completed_quantity=Avg('completed_quantity'),
#         average_production_quantity=Avg('production_quantity'),
#         average_cancelled_quantity=Avg('cancelled_quantity')
#     ).order_by('week')

#     # Calculate start and end dates for each week
#     for entry in weekly_stats:
#         start_date = entry['start_date']
#         end_date = entry['end_date']
#         year, week_num, _ = start_date.isocalendar()
#         entry['start_date'] = start_date
#         entry['end_date'] = end_date

#     traces = []

#     # Add traces for selected columns
#     if selected_columns is None or 'order_quantity' in selected_columns:
#         total_order_quantity = [int(entry['total_order_quantity']) for entry in weekly_stats]
#         trace_total_order_quantity = go.Bar(x=months, y=total_order_quantity, name='Total Order Quantity')
#         traces.append(trace_total_order_quantity)
    
#     if selected_columns is None or 'completed_quantity' in selected_columns:
#         total_completed_quantity = [int(entry['total_completed_quantity']) for entry in weekly_stats]
#         trace_total_completed_quantity = go.Bar(x=weeks, y=total_completed_quantity, name='Total Completed Quantity')
#         traces.append(trace_total_completed_quantity)
    
#     if selected_columns is None or 'cancelled_quantity' in selected_columns:
#         total_cancelled_quantity = [int(entry['total_cancelled_quantity']) for entry in weekly_stats]
#         trace_total_cancelled_quantity = go.Bar(x=months, y=total_cancelled_quantity, name='Total Cancelled Quantity')
#         traces.append(trace_total_cancelled_quantity)
    
#     if selected_columns is None or 'production_quantity' in selected_columns:
#         total_production_quantity = [int(entry['total_production_quantity']) for entry in weekly_stats]
#         trace_total_production_quantity = go.Bar(x=months, y=total_production_quantity, name='Total Production Quantity')
#         traces.append(trace_total_production_quantity)

#     # Create a Plotly figure
#     fig = go.Figure(data=traces)

#     # Update layout
#     fig.update_layout(title='Monthly Statistics',
#                       xaxis=dict(title='Wek'),
#                       yaxis=dict(title='Quantity'))

#     # Convert figure to HTML
#     plot_div = fig.to_html(full_html=False)

#     return weekly_stats,plot_div

import plotly.graph_objs as go

def weekly_statistics(product_id, from_date=None, to_date=None, selected_columns=None):
    # Filter the queryset by product_id and date range
    weekly_stats = ProductStatistics.objects.filter(product_id=product_id).order_by('date')
    if from_date and to_date:
        weekly_stats = weekly_stats.filter(date__range=[from_date, to_date])
    
    # Annotate the queryset to calculate week number, start date, and end date
    weekly_stats = weekly_stats.annotate(
        week=ExtractWeek('date'),
        start_date=Min('date'),
        end_date=Max('date')
    ).values('week', 'start_date', 'end_date').annotate(
        total_order_quantity=Cast(Sum('order_quantity'), IntegerField()),
        total_completed_quantity=Cast(Sum('completed_quantity'), IntegerField()),
        total_production_quantity=Cast(Sum('production_quantity'), IntegerField()),
        total_cancelled_quantity=Cast(Sum('cancelled_quantity'), IntegerField()),
        average_order_quantity=Cast(Avg('order_quantity'), IntegerField()),
        average_completed_quantity=Cast(Avg('completed_quantity'), IntegerField()),
        average_production_quantity=Cast(Avg('production_quantity'), IntegerField()),
        average_cancelled_quantity=Cast(Avg('cancelled_quantity'), IntegerField())
    ).order_by('week')

    # Calculate start and end dates for each week
    start_date = from_date if from_date else weekly_stats.first()['start_date']
    end_date = to_date if to_date else weekly_stats.last()['end_date']

    current_date = start_date
    weeks = []
    while current_date <= end_date:
        end_of_week = current_date + timedelta(days=6)
        weeks.append(f"{current_date.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}")
        current_date += timedelta(weeks=1)

    traces = []

    # Add traces for selected columns
    if selected_columns is None or 'order_quantity' in selected_columns:
        total_order_quantity = [int(entry['total_order_quantity']) for entry in weekly_stats]
        trace_total_order_quantity = go.Bar(x=weeks, y=total_order_quantity, name='Total Order Quantity')
        average_order_quantity = [int(entry['average_order_quantity']) for entry in weekly_stats]
        trace_average_order_quantity = go.Bar(x=weeks, y=average_order_quantity, name='Average Order Quantity')
        traces.append(trace_total_order_quantity)
        traces.append(trace_average_order_quantity)
    
    if selected_columns is None or 'completed_quantity' in selected_columns:
        total_completed_quantity = [int(entry['total_completed_quantity']) for entry in weekly_stats]
        trace_total_completed_quantity = go.Bar(x=weeks, y=total_completed_quantity, name='Total Completed Quantity')
        average_completed_quantity = [int(entry['average_completed_quantity']) for entry in weekly_stats]
        trace_average_completed_quantity = go.Bar(x=weeks, y=average_completed_quantity, name='Average Completed Quantity')
        traces.append(trace_total_completed_quantity)
        traces.append(trace_average_completed_quantity)
    
    if selected_columns is None or 'cancelled_quantity' in selected_columns:
        total_cancelled_quantity = [int(entry['total_cancelled_quantity']) for entry in weekly_stats]
        trace_total_cancelled_quantity = go.Bar(x=weeks, y=total_cancelled_quantity, name='Total Cancelled Quantity')
        average_cancelled_quantity = [int(entry['average_cancelled_quantity']) for entry in weekly_stats]
        trace_average_cancelled_quantity = go.Bar(x=weeks, y=average_cancelled_quantity, name='Average Cancelled Quantity')
        traces.append(trace_total_cancelled_quantity)
        traces.append(trace_average_cancelled_quantity)
    
    if selected_columns is None or 'production_quantity' in selected_columns:
        total_production_quantity = [int(entry['total_production_quantity']) for entry in weekly_stats]
        trace_total_production_quantity = go.Bar(x=weeks, y=total_production_quantity, name='Total Production Quantity')
        average_production_quantity = [int(entry['average_production_quantity']) for entry in weekly_stats]
        trace_average_production_quantity = go.Bar(x=weeks, y=average_production_quantity, name='Average Production Quantity')
        traces.append(trace_total_production_quantity)
        traces.append(trace_average_production_quantity)

    # Create a Plotly figure
    fig = go.Figure(data=traces)

    # # Update layout
    # fig.update_layout(title='Weekly Statistics',
    #                   xaxis=dict(title='Date Range', tickangle=90),
    #                   yaxis=dict(title='Quantity'),
    #                   xaxis_rangeslider_visible=True,
    #                   )

   
    
    
    fig.update_layout(title='Weekly Statistics',
                      xaxis=dict(title='Date Range', tickangle=90),
                      yaxis=dict(title='Quantity'),
                      xaxis_rangeslider_visible=True,
                       autosize=True, height=600,legend=dict(
            x=5.1,  # Set x position (1.1 places the legend slightly to the right of the plot)
            y=1.0   # Set y position (1.0 places the legend at the top of the plot)
        ))
    
    
    
    # Convert figure to HTML
    plot_div = fig.to_html(full_html=False)

    return weekly_stats, plot_div

def get_week_dates(year, week):
    d = datetime(year, 1, 1)
    if d.weekday() <= 3:
        d = d - timedelta(days=d.weekday())
    else:
        d = d + timedelta(days=7 - d.weekday())
    
    dlt = timedelta(days=(week - 1) * 7)
    start_date = d + dlt
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def count_total_quantities(product_id):
    total_order_quantity = ProductStatistics.objects.filter(product_id=product_id).aggregate(total_order_quantity=Sum('order_quantity'))['total_order_quantity'] or 0
    total_completed_quantity = ProductStatistics.objects.filter(product_id=product_id).aggregate(total_completed_quantity=Sum('completed_quantity'))['total_completed_quantity'] or 0
    total_cancelled_quantity = ProductStatistics.objects.filter(product_id=product_id).aggregate(total_cancelled_quantity=Sum('cancelled_quantity'))['total_cancelled_quantity'] or 0
    total_production_quantity = ProductStatistics.objects.filter(product_id=product_id).aggregate(total_production_quantity=Sum('production_quantity'))['total_production_quantity'] or 0

  

    avg_difference_order_completed = total_order_quantity - total_completed_quantity
    if total_order_quantity != 0:
        percentage_order_completed = (avg_difference_order_completed / total_order_quantity) * 100
    else:
        percentage_order_completed = 0
    avg_difference_order_production = total_production_quantity - total_order_quantity
    if total_order_quantity != 0:
        percentage_order_production = (avg_difference_order_production / total_order_quantity) * 100
    else:
        percentage_order_production = 0

    percentage_order_completed = round(percentage_order_completed, 3)
    percentage_order_production = round(percentage_order_production, 3)

    return {
        'total_order_quantity': total_order_quantity,
        'total_completed_quantity': total_completed_quantity,
        'total_cancelled_quantity': total_cancelled_quantity,
        'total_production_quantity': total_production_quantity,
        'percentage_order_completed':percentage_order_completed,
        'percentage_order_production':percentage_order_production
    }

def avg_prod_order_diff(product_id):

    # Retrieve ProductStatistics instances for the selected product
    product_stats = ProductStatistics.objects.filter(product_id=product_id)
    int_order_quantity = 0

    for col in product_stats:
        int_order_quantity += int(col.order_quantity)
    print("test",int_order_quantity)


def productStatistics(request):

    if request.method == 'GET':
        # current_user_id = request.user.id
        current_user_id = request.user.added_by
        categories = category.objects.filter(userid=request.user)
        products = []  # Placeholder for products

        # Calculate the start date as the latest date available in ProductStatistics
        latest_date_entry = ProductStatistics.objects.latest('date').date if ProductStatistics.objects.exists() else date(2024, 2, 1)
        end_date = date.today() - timedelta(days=1)  # Yesterday's date
        start_date = latest_date_entry + timedelta(days=1)

        # Generate statistics for each date within the range
        for dt in daterange(start_date, end_date):
            generate_statistics_for_date(current_user_id,dt)

        # If start_date is after yesterday, generate statistics only for today
        if start_date > end_date:
            generate_statistics_for_date(current_user_id,date.today())

        # Retrieve products filtered by category if provided in the request
        if 'category_id' in request.GET:
            category_id = request.GET.get('category_id')
            if category_id:
                products = Product.objects.filter(category_id=category_id)

        # Retrieve all product statistics
        product_statistics = ProductStatistics.objects.all()

        product_id = request.GET.get('product')
        
        print(request.POST)
        if product_id:
            avg_prod_order_diff(product_id)
            product = Product.objects.get(product_id=product_id) 
            product_name = product.product_name
            
            from_date_str = request.GET.get('from_date')
            to_date_str = request.GET.get('to_date')

            frequency = request.GET.get('time_interval')    
            print("frequency",frequency)

            selected_columns_str = request.GET.get('selected_columns')
            selected_columns = selected_columns_str.split(',') if selected_columns_str else []
            print("first",selected_columns)

            from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

                        

            product_statistics = ProductStatistics.objects.filter(product_id=product_id).order_by('date')
            if from_date and to_date:
                product_statistics = product_statistics.filter(date__range=[from_date, to_date])

            print("product_id", product_id)
           
            if frequency == 'daily':
                print("selected", frequency)
                daily_stats_data, plot_div = daily_statistics(product_id, from_date, to_date, selected_columns)
                monthly_stats = None
                weekly_stats = None
                plot_div_monthly =None
                selected_columns_monthly = None
                plot_div_weekly=None
            elif frequency == 'monthly':
                # monthly_stats= monthly_statistics(product_id, from_date, to_date)
                plot_div_monthly, monthly_stats,selected_columns_monthly = monthly_statistics(product_id, from_date, to_date, selected_columns)
                plot_div = None
                weekly_stats = None
                plot_div_weekly =None
                daily_stats_data=None
            elif frequency == 'weekly':
                weekly_stats, plot_div_weekly= weekly_statistics(product_id, from_date, to_date, selected_columns)
                plot_div = None
                monthly_stats = None
                plot_div_monthly =None
                daily_stats_data=None
            totals_products = count_total_quantities(product_id)
           

           
        else:
            product_statistics = ProductStatistics.objects.all()
            plot_div = None
            monthly_stats = None
            plot_div_monthly =None
            frequency = None
            plot_div = None
            monthly_stats = None
            plot_div_monthly =None
            totals_products=None
            weekly_stats = None
            plot_div_weekly =None
            selected_columns=None
            product_name=None
            daily_stats_data=None


        # Add pending and ongoing quantities to context
        context = {
            'product_statistics': product_statistics,
            'categories': categories,
            'products': products,
            'plot_div': plot_div,
            'monthly_stats': monthly_stats,
            'plot_div_monthly':plot_div_monthly,
            'selected_columns':selected_columns,
            'weekly_stats': weekly_stats,
            'plot_div_weekly':plot_div_weekly,
            'totals_products': totals_products,
            'frequency':frequency,
            'product_name':product_name,
            'daily_stats_data':daily_stats_data
            }
        return render(request, 'product_statistics.html', context)

def get_products(request):
    category_id = request.GET.get('category') 
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    data = [{'product_id': product.product_id, 'product_name': product.product_name} for product in products]
    return JsonResponse(data, safe=False)


def generate_statistics_for_date(current_user_id, current_date):
    # Get all products for the current user
    user_products = Product.objects.filter(user_id=current_user_id)
    
    # Iterate over each product
    for product in user_products:
        # Check if statistics already exist for the current date and product
        existing_statistic = ProductStatistics.objects.filter(user_id=current_user_id, product_id=product.product_id, date=current_date).first()
        if not existing_statistic:
            product_statistic = ProductStatistics.objects.create(
                user_id=current_user_id,
                product_id=product.product_id,
                date=current_date,
                order_quantity=0,
                completed_quantity=0,
                cancelled_quantity=0,

                production_quantity=0,
                deduction_quantity=0
            )

            
            product_statistic.save()


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


@login_required
def staff(request):
    current_user_id = request.user.id
    search_query = request.GET.get('search_query')
    
    # Fetch all staff members
    staff_members = CustomUser.objects.filter(added_by=current_user_id, deleted_on__isnull=True)
    
    if search_query:
        staff_members = staff_members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(userrole__icontains=search_query)
        )
        context = {
        'staff_members': staff_members,
        'search_query': search_query
    }
    else:
    
        # Paginate the results
        paginator = Paginator(staff_members, 20)  # 20 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'staff_members': page_obj,
            'search_query': search_query
        }
            
    
    return render(request, 'staff.html', context)

@login_required




def addStaff(request):
    if request.method == 'POST':
        current_user = request.user.id

        fname = request.POST.get('first_name', '')
        lname = request.POST.get('last_name', '')
        email = request.POST.get('staff_email', '')
        password = 'ofs@12345'  
        phone = request.POST.get('staff_phone', '')
        role = request.POST.get('staff_role', '')

        # Validate phone number length
        if len(phone) != 10:
            messages.error(request, 'Failed! Phone number must be 10 digits.')
            return HttpResponseRedirect('/staff')

        try:
            # Create a new CustomUser (staff member)
            user = CustomUser.objects.create_user(
                username=email,
                company_id=current_user,
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

def deactivatedStaff(request):
    current_user_id = request.user.id
    search_query = request.GET.get('search_query')
    
    # Fetch all deactivated staff members where deleted_on is null
    staffs = CustomUser.objects.filter(added_by=current_user_id, deleted_on__isnull=False)
    
    if search_query:
        staffs = staffs.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(userrole__icontains=search_query)
        )
        context = {
            'staff_members': staffs,
            'search_query': search_query
        }
    else:
        # Paginate the results
        paginator = Paginator(staffs, 20)  # 20 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'staff_members': page_obj,
            'search_query': search_query
        }
            
    return render(request, 'deactivatedstaff.html', context)
@login_required
def editStaff(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id', '')
        fname = request.POST.get('edit_first_name', '')
        lname = request.POST.get('edit_last_name', '')
        email = request.POST.get('edit_staff_email', '')
        phone = request.POST.get('edit_staff_phone', '')
        role = request.POST.get('edit_staff_role', '')

        # Validate phone number length
        if len(phone) != 10:
            messages.error(request, 'Failed! Phone number must be 10 digits.')
            return HttpResponseRedirect('/staff')

        try:
            # Get the existing staff member by ID
            staff_member = CustomUser.objects.get(id=staff_id)

            # Check if any data has been changed
            if staff_member.first_name == fname and staff_member.last_name == lname and staff_member.email== email and staff_member.phone_number== phone and staff_member.userrole== role:
                messages.info(request, f'No data has been changed for staff {staff_member.first_name} {staff_member.last_name}.')
            else:
                # Update the staff member information
                staff_member.first_name = fname
                staff_member.last_name = lname
                staff_member.email = email
                staff_member.phone_number = phone
                staff_member.userrole = role
                staff_member.save()

                messages.success(request, 'Staff member information updated successfully!')

            return HttpResponseRedirect('/staff')

        except CustomUser.DoesNotExist:
            messages.error(request, 'Staff member does not exist.')
            return HttpResponseRedirect('/staff')
        except IntegrityError:
            messages.error(request, 'Email already exists. Please use a different email address.')
            return HttpResponseRedirect('/staff')

    return render(request, 'staff.html')


from django.urls import reverse


@login_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, id=staff_id)
    staff.deleted_on = timezone.now()
    staff.save()
    messages.success(request, f"Successfully Deactivated Staff: {staff.first_name} {staff.last_name}.")
    return render(request, 'staff.html')

@login_required
def reactivate_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, id=staff_id)
    staff.deleted_on = None
    staff.save()
    messages.success(request, f"Successfully Reactivated Staff: {staff.first_name} {staff.last_name}.")
    return render(request, 'staff.html')

from .models import category, Product, InventoryDetails, InventoryDetailsDate, Order,CustomUser,ForecastData,ProductStatistics  



@login_required

def get_category(request):
    current_user_id = request.user.added_by
    categories = category.objects.filter(userid=current_user_id)
    search_query = request.GET.get('q')

    if search_query:
        categories = categories.filter(Q(category__icontains=search_query) | Q(id__icontains=search_query))

    # Paginate categories
    paginator = Paginator(categories, 20)
    page = request.GET.get('page')

    try:
        paginated_categories = paginator.page(page)
    except PageNotAnInteger:
        paginated_categories = paginator.page(1)
    except EmptyPage:
        paginated_categories = paginator.page(paginator.num_pages)

    context = {
        'categories': paginated_categories,
        'search_query': search_query,
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
    current_user = request.user.added_by

    products = Product.objects.filter(user_id=current_user, deleted_on__isnull=True).order_by('-id')
    categories = category.objects.filter(userid_id=current_user)
    search_query = request.GET.get('q')

    # Initialize products_search
    products_search = None

    if search_query:
        products_search = products.filter(
            Q(product_id__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query) |
            Q(category__category__icontains=search_query)
        )
        context = { 
            'search_query': search_query,
            'products': products_search,
            'categories': categories,
        }


    else:
        # Paginate all products
        paginator = Paginator(products, 20)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)

        context = { 
            'products': products,
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

            # if existing_product:
            #     existing_product.deleted_on = None
            #     existing_product.save()
            #     messages.success(request, 'Product added successfully!')
            # else:
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

# def getOrder(request):
#     current_user = request.user

#     orders = Order.objects.filter(
#         user_id=current_user,
#         status__in=['Ongoing', 'Pending'],
#         deleted_on__isnull=True
#     ).select_related('product').order_by('-id')

#     for order in orders:
#         delivery_date = order.delivery_date
#         current_date = timezone.now().date()

#         if delivery_date < current_date:
#             order.status = 'Pending'
#             order.save()
#         elif delivery_date == current_date or delivery_date > current_date:
#             order.status = 'Ongoing'
#             order.save()

#     search_query = request.GET.get('q')

#     if search_query:
#         orders = orders.filter(
#             Q(order_id__icontains=search_query) |
#             Q(quantity__icontains=search_query) |
#             Q(ordered_date__icontains=search_query) |
#             Q(delivery_date__icontains=search_query) |
#             Q(completed_date__icontains=search_query) |
#             Q(price__icontains=search_query) |
#             Q(status__icontains=search_query) |
#             Q(product__product_name__icontains=search_query)  # Search by product name (assuming it's a field in Product)
#         )
#     page = request.GET.get('page', 1)
#     paginated_orders = paginate_data(orders, page, 20)
#     context = {
#         'orders': paginated_orders,
#     }

#     return render(request, 'orders.html', context)

def getOrder(request):
    categories = category.objects.filter(userid=request.user)
    current_user = request.user

    # Retrieve all orders for the current user with status 'Ongoing' or 'Pending' and not deleted
    orders = Order.objects.filter(
        user_id=current_user,
        status__in=['Ongoing', 'Pending'],
        deleted_on__isnull=True
    ).select_related('product').order_by('-id')

    # Update the status of orders based on delivery date
    current_date = timezone.now().date()
    for order in orders:
        delivery_date = order.delivery_date
        if delivery_date < current_date:
            order.status = 'Pending'
            order.save()
        elif delivery_date >= current_date:
            order.status = 'Ongoing'
            order.save()

    search_query = request.GET.get('q')

    if search_query:
        # Filter orders based on the search query
        orders_search = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)  # Search by product name (assuming it's a field in Product)
        )


        # No pagination for search results
        context = {
            'orders': orders_search,
            'search_query': search_query,
            'categories':categories
        }
    else:
        # Paginate orders for display
        page = request.GET.get('page', 1)
        paginated_orders = paginate_data(orders, page, 20)
        context = {
            'orders': paginated_orders,
            'categories':categories
        }

    return render(request, 'orders.html', context)

def get_products_by_category(request):
    category_id = request.GET.get('categorySelect_order_filter')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
        product_options = ''
        for product in products:
            product_options += f'<option value="{product.product_id}">{product.product_name}</option>'
        return JsonResponse({'products': product_options})
    return JsonResponse({'products': ''})


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

            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)  # Search by product name (assuming it's a field in Product)
        )
        for order in paginated_orders:
            order.ordered_date = order.ordered_date.strftime("%b %d, %Y")
            order.delivery_date = order.delivery_date.strftime("%b %d, %Y")
            order.completed_date = order.completed_date.strftime("%b %d, %Y")

        context = {
            'orders': completed_orders,
            'search_query': search_query,
        }
    else:
        page = request.GET.get('page', 1)
        paginated_orders = paginate_data(completed_orders, page, 20)

        context = {
            'orders': paginated_orders,
            'search_query':search_query,
        }

    return render(request, 'completedorder.html', context)

@login_required

def getCancelledOrder(request):
    current_user_id = request.user.added_by

    cancelled_orders = Order.objects.filter(user_id=current_user_id, status='Cancelled').order_by('-id')
    
    search_query = request.GET.get('q')


    if search_query:
        cancelled_orders = cancelled_orders.filter(
            Q(order_id__icontains=search_query) |
            Q(quantity__icontains=search_query) |

            Q(price__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(product__product_name__icontains=search_query)

        )
        context = {
            'orders': cancelled_orders,
            'search_query': search_query,
        }
    else:
        page = request.GET.get('page', 1)
        paginated_orders = paginate_data(cancelled_orders, page, 20)

        context = {
            'orders': paginated_orders,
            'search_query': search_query,
        }

    return render(request, 'cancelledorder.html', context)

@login_required
# def order_filter(request):
#     if request.method == 'POST':
#         basedon = request.POST.get('basedon')
#         from_date = request.POST.get('from-date')
#         to_date = request.POST.get('to-date')
#         max_price = request.POST.get('max-price')
#         min_price = request.POST.get('min-price')
#         max_quantity = request.POST.get('max-quantity')
#         min_quantity = request.POST.get('min-quantity')

#         filter_params = {
#             'user_id': request.user,
#         }

#         if from_date:
#             filter_params[f'{basedon}__gte'] = from_date
#         if to_date:
#             filter_params[f'{basedon}__lte'] = to_date
#         if min_price:
#             filter_params['price__gte'] = min_price
#         if max_price:
#             filter_params['price__lte'] = max_price
#         if min_quantity:
#             filter_params['quantity__gte'] = min_quantity
#         if max_quantity:
#             filter_params['quantity__lte'] = max_quantity

#         filtered_orders = Order.objects.filter(
#             Q(user_id=request.user),
#             **filter_params
#         )

#         context = {
           
#             'orders':filtered_orders
#         }
#             # filteredList.append(context)

#         return render(request, 'orders.html', context)

#     return HttpResponseRedirect('/orders')

def order_filter(request):
    if request.method == 'POST':
        basedon = request.POST.get('basedon')
        from_date = request.POST.get('from-date')
        to_date = request.POST.get('to-date')
        max_price = request.POST.get('max-price')
        min_price = request.POST.get('min-price')
        max_quantity = request.POST.get('max-quantity')
        min_quantity = request.POST.get('min-quantity')
        status = request.POST.get('status')
        category_id = request.POST.get('categorySelect_order_filter')
        product_id = request.POST.get('product')

        filter_params = {
            'user_id': request.user,
            'product__deleted_on__isnull': True,  # Exclude deleted products
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
        if status:
            filter_params['status'] = status
        if category_id:
            filter_params['product__category_id'] = category_id
        if product_id:
            filter_params['product_id'] = product_id

        filtered_orders = Order.objects.filter(
            Q(user_id=request.user),
            **filter_params
        )
        categories = category.objects.filter(userid_id=request.user.id)
        print("categories",categories)
        products = []  # Initially, no products until a category is selected

        context = {
            'orders': filtered_orders,
            'categories': categories
        }

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
        if value is not None and value < 1:
            raise ValueError(f"{field_name.capitalize()} cannot be 0 or less than 0.")


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
        previous_page = request.META.get('HTTP_REFERER')

        # Convert dates to datetime objects
        ordered_date = timezone.datetime.strptime(ordered_date, '%Y-%m-%d').date()
        delivery_date = timezone.datetime.strptime(delivery_date, '%Y-%m-%d').date()
        try:
            check_negative_values({
            'Quantity': Decimal(quantity),
            })
        except ValueError as ve:
            messages.error(request, str(ve))
            return HttpResponseRedirect(previous_page)
        
        if delivery_date <= ordered_date:
            messages.error(request, 'Delivery date must be later than the order date.')
            return HttpResponseRedirect(previous_page)

        # Fetch price from InventoryDetailsDate based on product_id and ordered_date
        try:
            inventory_entry = InventoryDetailsDate.objects.get(product__product_id=order_product_name,
                                                               date=ordered_date,
                                                               user=current_user_id)
            price = inventory_entry.price
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
                available_quanity = latest_inventory_entry.quantity
                
            except InventoryDetailsDate.DoesNotExist:
                messages.error(request, f'Price not found for the specified {product_name}.')
                price = 0
                total_price = 0
        latest_inventory_entry_quantity = InventoryDetailsDate.objects.filter(
            product__product_id=order_product_name,
            user=current_user_id
        ).latest('date')

        available_quantity = Decimal(latest_inventory_entry_quantity.quantity)

        

        # Check if the requested quantity exceeds the available quantity
        if status == "Completed":
            if Decimal(quantity) > available_quantity:
                messages.error(request, f"Requested quantity exceeds available quantity.")
                return HttpResponseRedirect(previous_page)
     
   
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
                order.completed_date = timezone.now().date()

                order.save()
            if status.lower() == 'cancelled':
                order.cancelled_date = timezone.now().date()
                order.save()

            inventory_quantity, created_quantity = InventoryDetailsDate.objects.get_or_create(product__product_id=order_product_name,
                                                                           date=timezone.now().date(),
                                                                           user=current_user_id)
            
            
            product_statistic_order_quantity, created = ProductStatistics.objects.get_or_create(product_id=order_product_name, date = ordered_date)

            quantity_int = int(quantity) if quantity else 0

            # Update order quantity
            product_statistic_order_quantity.order_quantity = str(int(product_statistic_order_quantity.order_quantity or 0) + quantity_int)
            product_statistic_order_quantity.save()

            if status.lower() == 'completed':
                        # Get the current date
                        current_date = timezone.now().date()
                        if created_quantity:
                            inventory_quantity.quantity = str(int(order.quantity)) 
                            inventory_quantity.quantity_deducted = str(int(order.quantity))
                            inventory_quantity.save()
                        else:
                            inventory_quantity.quantity = str(int(available_quantity)-int(order.quantity)) 
                            inventory_quantity.quantity_deducted = str(int(inventory_quantity.quantity_deducted) + int(order.quantity))
                            inventory_quantity.save()


                        # Get or create the ProductStatistic object
                        product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=current_date)

                        # Update the completed quantity
                        product_stat.completed_quantity = str(int(product_stat.completed_quantity or 0) + int(order.quantity))
                        print(product_stat.completed_quantity)
                        product_stat.save()
                        print("status save",product_stat.save())

                        # Provide success message based on status
                        
            elif status.lower() == 'cancelled':
                # Get the current date
                current_date = timezone.now().date()

                # Get or create the ProductStatistic object
                product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=current_date)

                # Update the completed quantity
                product_stat.cancelled_quantity = str(int(product_stat.cancelled_quantity or 0) + int(order.quantity))
                product_stat.save()



            messages.success(request, f"Statistics updated for product: {order.product.product_name}.")
                
            messages.success(request, 'New Order Added')

            
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
        

        old_quantity=int(order.quantity )
        old_price=order.price
        old_delivery_date=order.delivery_date 
        old_ordered_date=order.ordered_date
        old_status=order.status 

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
            # return redirect(request.session['referring_page'])

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
                messages.error(request, f"Cannot complete order {old_order_id}. Requested quantity exceeds available quantity.")
                return redirect(request.session['referring_page'])      

        # Update the order details
        order.quantity = Decimal(edit_quantity)
        order.price = Decimal(edit_price)
        order.total_price = Decimal(edit_quantity) * Decimal(edit_price)
        order.delivery_date = edit_delivery_date
        order.ordered_date = edit_ordered_date
        order.status = edit_status
        order.updated_on =datetime.now()

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            try:
                if edit_status.lower() == 'completed':
                    order.completed_date = timezone.now().date()
                if edit_status.lower() == 'cancelled':
                    order.cancelled_date = timezone.now().date()
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
                        user=current_user_id,
                        date=latest_date
                    ).update(
                        quantity=F('quantity') - Decimal(edit_quantity)
                    )
                    messages.success(request,f"Inventory Updated for product: {order.product.product_name}.")

                print("old_quantity", old_quantity)
                print("new quantity", order.quantity)
                print("type of old_quantity:", type(int(order.quantity)))
                
                if order.ordered_date != old_ordered_date and order.quantity != old_quantity:
                    
                    old_product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=old_ordered_date)
                    old_product_stat.order_quantity = str(int(old_product_stat.order_quantity or 0) - int(old_quantity))
                    old_product_stat.save()

                    # Add quantity to new order date
                    new_product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=order.ordered_date)
                    new_product_stat.order_quantity = str(int(new_product_stat.order_quantity or 0) + int(order.quantity))
                    new_product_stat.save()
                    messages.success(request,f"Statistics Updated for product: {order.product.product_name}.")

                elif order.ordered_date != old_ordered_date:
                    # If only order date changed
                    # Deduct quantity from old order date
                    old_product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=old_ordered_date)
                    old_product_stat.order_quantity = str(int(old_product_stat.order_quantity or 0) - int(old_quantity))
                    old_product_stat.save()

                    # Add quantity to new order date
                    new_product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=order.ordered_date)
                    new_product_stat.order_quantity = str(int(new_product_stat.order_quantity or 0) + int(old_quantity))  # Adding the old quantity
                    new_product_stat.save()
                    messages.success(request,f"Statistics Updated for product: {order.product.product_name}.")

                elif order.quantity != old_quantity:
                    # If only quantity changed
                    product_stat, created = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=order.ordered_date)
                    product_stat.order_quantity = str(int(product_stat.order_quantity or 0) - (int(order.quantity) - int(old_quantity)))
                    product_stat.save()
                    messages.success(request,f"Statistics Updated for product: {order.product.product_name}.")

                
                if edit_status != old_status:
                    if edit_status.lower() == 'completed':
                        # Get the current date
                        current_date = timezone.now().date()

                        # Get or create the ProductStatistic object
                        product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=current_date)

                        # Update the completed quantity
                        product_stat.completed_quantity = str(int(product_stat.completed_quantity or 0) + int(order.quantity))
                        product_stat.save()
                        print("status save",product_stat.save())

                        # Provide success message based on status
                        messages.success(request, f"Completed quantity updated for product: {order.product.product_name}.")
                    elif edit_status.lower() == 'cancelled':
                        # Get the current date
                        current_date = timezone.now().date()

                        # Get or create the ProductStatistic object
                        product_stat, _ = ProductStatistics.objects.get_or_create(product_id=order.product_id, date=current_date)

                        # Update the completed quantity
                        product_stat.cancelled_quantity = str(int(product_stat.cancelled_quantity or 0) + int(order.quantity))
                        product_stat.save()
                        messages.success(request, f"Cancelled quantity updated for product: {order.product.product_name}.")

                    

                messages.success(request, 'New Order Added')
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
            if product_stat:
                deleted_quantity = (product_stat.deleted_quantity or 0) + order.quantity                
                ProductStatistics.objects.filter(pk=product_stat.pk).update(deleted_quantity=deleted_quantity)
                
            else:
                ProductStatistics.objects.create(date=today, product_id=product_id, deleted_quantity=order.quantity)
            messages.success(request,f"Statistics Updated for product: {order.product.product_name}.")
            
            order.deleted_on = datetime.now()
            order.save()

            today = datetime.now()
            product_stat = ProductStatistics.objects.filter(date=today, product_id=product_id).first()

            
            
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

    # # Retrieve products and inventory details after adding the required data
    # products = Product.objects.filter(category_id=category_id, user_id=current_user_id, deleted_on__isnull=True).values('product_id', 'product_name')
    # product_ids = [str(product['product_id']) for product in products]

    inventory_details = InventoryDetailsDate.objects.filter(
        product__product_id__in=product_ids,
        user_id=current_user_id
    ).order_by('-id')

    products_list = list(products)
    # inventory_list = list(inventory_details)
    if search_query:
        # Apply search query to filter inventory details
        inventory_items = inventory_details.filter(
            Q(product__product_name__icontains=search_query) |
            Q(quantity__icontains=search_query) |
            Q(quantity_added__icontains=search_query) |
            Q(quantity_deducted__icontains=search_query) |
            Q(price__icontains=search_query)
        )
        context = {
            'product': products_list,
            'category_name':category_name,
            'search_query':search_query,
            'items': inventory_items
        }
    else:
        inventory_items = inventory_details


        
        page = request.GET.get('page', 1)
        paginated_items = paginate_data(inventory_items, page, 20)

        context = {
            'items': paginated_items,
            'product': products_list,
            'category_name':category_name,
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
            # Update product statistics
            ProductStatistics.objects.update_or_create(
                product_id=product,
                date=current_date,
                defaults={
                    'production_quantity': F('production_quantity') + int(quantity)
                }
            )
            messages.success(request, f"Statistics updated for product: {existing_data_history.product.product_name}.")
        except Exception as e:
            messages.error(request, f"Error updating product statistics: {str(e)}")
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
            product_id = existing_data_history.product_id
            date = existing_data_history.date

            if quantity_added != "":
                new_quantity_added = existing_quantity_added + quantity_added
            else:
                new_quantity_added = existing_quantity_added
                quantity_added = 0

         
                
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

                product_statistic, created = ProductStatistics.objects.get_or_create(date=date, product_id=product)
                product_statistic.production_quantity = str(int(product_statistic.production_quantity or 0) + int(quantity_added))
                product_statistic.deduction_quantity = str(int(product_statistic.deduction_quantity or 0) + int(quantity_deducted))

                product_statistic.save()
                messages.success(request, f"Statistics updated for product: {existing_data_history.product.product_name}.")
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

# def arima_sarimax_forecast(data):
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

#     # Get the current date
#     current_date = datetime.now()

#     # Forecast for the next 12 months from the current month
#     forecast_steps = 12 - current_date.month + 1  # Adjusting for the current month

#     # Forecast using ARIMA
#     arima_forecast = arima_result.get_forecast(steps=forecast_steps)
#     arima_confidence_intervals = arima_forecast.conf_int()

#     # Forecast using SARIMAX
#     sarimax_forecast = sarimax_result.get_forecast(steps=forecast_steps)
#     sarimax_confidence_intervals = sarimax_forecast.conf_int()

#     return {
#         'arima_forecast': arima_forecast.predicted_mean,
#         'arima_confidence_intervals': arima_confidence_intervals,
#         'sarimax_forecast': sarimax_forecast.predicted_mean,
#         'sarimax_confidence_intervals': sarimax_confidence_intervals,
#     }

def arima_sarimax_forecast(data):
    # Convert 'Month' column to datetime format if not already
    data['Month'] = pd.to_datetime(data['Month'])

    # Set 'Month' as the index
    data.set_index('Month', inplace=True)

    # Perform first-order differencing to make the time series stationary
    data_diff = data['Sales'].diff().dropna()

    # Perform seasonal differencing if necessary
    seasonal_diff = data_diff.diff(periods=30).dropna()

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

    # Forecast for the next 30 days from the current date
    forecast_steps = 30

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
