import datetime

import requests
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import generic

# Create your views here.
from .forms import CreateUserForm
from .models import City

@login_required(login_url='loginpage')
def index(request):
    API_KEY = "752667ff0ad1f03d7abff59e2f700d4b"
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"


    if request.method == "POST":
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)


        try:
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)

            if city2:
                weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_url)
            else:
                weather_data2, daily_forecasts2 = None, None
        except:
            return redirect('index')

        context = {
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
            "weather_data2": weather_data2,
            "daily_forecasts2": daily_forecasts2,

        }
        return render(request, "weather_app/index.html", context)

    else:
        return render(request, "weather_app/index.html")

@login_required(login_url='loginpage')
def favourites(request):
    API_KEY = "752667ff0ad1f03d7abff59e2f700d4b"
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"

    if request.method == "POST":
        city = request.POST['city']

        try:
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city, API_KEY, current_weather_url, forecast_url)
        except:
            return redirect('favourites')

        fav = City(user=request.user,name=city,temperature=weather_data1['temperature'],description=weather_data1['description'])
        fav.save()


        return render(request, "weather_app/favourites.html")
    else:
        for city2 in City.objects.filter(user=request.user):
            grad = city2.name
            weather_data3, daily_forecasts3 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url,forecast_url)
            city2.temperature = weather_data3['temperature']
            city2.description = weather_data3['description']
            city2.save()
        return render(request, "weather_app/favourites.html")

class favouritesView(generic.DetailView):
    model = City
    template_name="weather_app/favourites.html"


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):

    response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()


    weather_data = {
        "city": city,
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon']

    }

    daily_forecasts = []
    for daily_data in forecast_response['list'][:5]:
        daily_forecasts.append({
            "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
            "hour": daily_data['dt_txt'],
            "min_temp": round(daily_data['main']['temp_min'] - 273.15, 2),
            "max_temp": round(daily_data['main']['temp_max'] - 273.15, 2),
            "description": daily_data['weather'][0]['description'],
            "icon": daily_data['weather'][0]['icon']
        })

    return weather_data, daily_forecasts

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('loginpage')

        context = {
            'form': form
        }
        return render(request, "weather_app/register.html", context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.info(request, 'Username or password is incorrect')

        context = {}
        return render(request, "weather_app/login.html ", context)

def logoutUser(request):
    logout(request)
    return redirect('loginpage')