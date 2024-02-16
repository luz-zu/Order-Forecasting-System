
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
