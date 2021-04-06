from django.urls import path

from Users import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
]