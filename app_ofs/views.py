from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect
from .forms import RegisterForm



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/dashboard')
        else:
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