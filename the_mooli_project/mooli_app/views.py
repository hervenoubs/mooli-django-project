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
from django.urls import reverse
from .models import CustomUser, UserProfile
from django.contrib.auth.hashers import make_password
from .forms import RegistrationForm, CustomLoginForm
from django.contrib.auth.views import LoginView as DjangoLoginView

class LoginView(DjangoLoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        # Activate language from user profile
        profile = self.request.user.userprofile
        translation.activate(profile.default_language)
        self.request.session[translation.LANGUAGE_SESSION_KEY] = profile.default_language
        return response

@login_required
def dashboard(request):
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
        return render(request, 'activation_invalid.html')  # Create this template

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
        try:
            company = profile.companies.get(id=company_id)
            profile.current_company = company
            profile.save()
        except profile.companies.model.DoesNotExist:
            pass  # Handle invalid company_id
    return redirect('dashboard')

def forgot_password(request):
    if request.method == 'POST':
        # Password reset logic will appear here
        pass
    return render(request, 'forgot_password.html')