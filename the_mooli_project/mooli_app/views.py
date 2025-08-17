from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.utils import translation
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse, translate_url
from .models import CustomUser, UserProfile
from django.contrib.auth.hashers import make_password
from .forms import RegistrationForm, CustomLoginForm
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.utils.translation import activate as translation_activate, get_language_from_path
from urllib.parse import urlparse

class LoginView(DjangoLoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        
        # Activate user's preferred language
        try:
            profile = user.userprofile
            language = profile.default_language
            translation.activate(language)
            self.request.session[settings.LANGUAGE_SESSION_KEY] = language
            
            # Redirect to language-prefixed version of the dashboard
            redirect_url = f'/{language}/'  # Will redirect to /fr/
            return redirect(redirect_url)
            
        except UserProfile.DoesNotExist:
            # Fallback to default language
            translation.activate(settings.LANGUAGE_CODE)
            self.request.session[settings.LANGUAGE_SESSION_KEY] = settings.LANGUAGE_CODE
        
        return response

@login_required
def dashboard(request):
    # Ensure language is activated
    if request.user.is_authenticated:
        try:
            language = request.user.userprofile.default_language
            translation.activate(language)
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]  # Username from email

            user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False
            )
            user.password = make_password(password)
            user.save()

            profile = UserProfile.objects.create(
                user=user,
                default_language='en'
            )

            # Generate activation token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Set expiry
            profile.activation_key = token
            profile.activation_expiry = timezone.now() + timezone.timedelta(hours=1)
            profile.save()

            # Send activation email
            activation_link = request.build_absolute_uri(reverse('activate', args=[uidb64, token]))
            send_mail(
                'Activate Your Account',
                f'Click the link to activate your account: {activation_link}\nLink expires in 1 hour.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect('login')  # Redirect to login
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        profile = user.userprofile
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    token_generator = PasswordResetTokenGenerator()
    if user is not None and token_generator.check_token(user, token) and profile.activation_expiry > timezone.now():
        user.is_active = True
        user.save()
        profile.activation_key = None
        profile.activation_expiry = None
        profile.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'activation_invalid.html')

def set_language(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    next_url = request.GET.get('next', '/')
    
    if lang in dict(settings.LANGUAGES):
        # Update session
        request.session[settings.LANGUAGE_SESSION_KEY] = lang
        translation.activate(lang)
        
        # Update user profile if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                profile.default_language = lang
                profile.save()
            except Exception:
                pass
        
        # Handle the redirect URL
        if next_url == '/':
            next_url = f'/{lang}/'
        else:
            # Ensure the URL has the correct language prefix
            parts = next_url.split('/')
            if len(parts) > 1 and parts[1] in dict(settings.LANGUAGES):
                parts[1] = lang
                next_url = '/'.join(parts)
            else:
                next_url = f'/{lang}{next_url}'
    
    return redirect(next_url)

@login_required
def switch_company(request, company_id):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        try:
            company = profile.companies.get(id=company_id)
            profile.current_company = company
            profile.save()
        except profile.companies.model.DoesNotExist:
            pass  # Handle invalid company_id
    return redirect('dashboard')