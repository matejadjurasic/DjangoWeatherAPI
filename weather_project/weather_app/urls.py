from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registerPage, name="registerpage"),
    path('login/', views.loginPage, name="loginpage"),
    path('logout/', views.logoutUser, name="logoutpage"),
    path('favourites/', views.favourites, name="favourites"),
    path("", views.index, name="index")
]
