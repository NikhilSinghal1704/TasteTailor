from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name = "SignUp"),
    path('signin', views.signin, name = "SignIn"),
    path('signout', views.signout, name = "SignOut"),
    path('activate/<uidb64>/<token>/', views.activate, name = "Activate"),
    path('preferences', views.preferences, name = "preferences"),
    path('edit-preferences', views.edit_preferences, name = "edit_preferences"),
]