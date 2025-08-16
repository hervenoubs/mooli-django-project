from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import login
from django.utils import translation
from django.contrib.auth.decorators import login_required
from django.conf import settings

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"

@login_required
def dashboard(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        # Registration logic will appear here
        pass
    return render(request, 'register.html')

def forgot_password(request):
    if request.method == 'POST':
        # Password reset logic will appear here
        pass
    return render(request, 'forgot_password.html')

@login_required
def set_language(request):
    lang = request.GET.get('lang', 'en')
    if lang in dict(settings.LANGUAGES):
        translation.activate(lang)
        if request.user.is_authenticated:
            request.user.userprofile.default_language = lang
            request.user.userprofile.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def switch_company(request, company_id):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        profile.company_id = company_id
        profile.save()
    return redirect('dashboard')