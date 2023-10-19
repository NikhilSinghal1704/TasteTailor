from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('signup', views.signup, name = "SignUp"),
    path('signin', views.signin, name = "SignIn"),
    path('signout', views.signout, name = "SignOut"),
    path('activate/<uidb64>/<token>/', views.activate, name = "Activate"),
]