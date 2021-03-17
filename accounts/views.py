import os
import shutil

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as DjangoLogin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import resolve_url
from django.conf import settings

from misconduct_detection_app.env_settings import get_session_paths, get_user_paths


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        sess_paths = get_session_paths(self.request.session)
        logged_in_paths = get_user_paths(self.object)

        for sess_path, user_path in zip(sess_paths, logged_in_paths):
            if os.path.exists(sess_path):
                shutil.move(sess_path, user_path)
        
        return response

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))
        return super().get(request, *args, **kwargs)


class LoginView(DjangoLogin):
    redirect_authenticated_user = True
