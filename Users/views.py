from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from Users.forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class LoginView(CreateView):
    def reload(self, request):
        return render(request.path)


class LogoutView(CreateView):
    def reload(self, request):
        return render(request.path)
