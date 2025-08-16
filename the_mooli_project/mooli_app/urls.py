from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
  path('', views.dashboard, name='dashboard'),
  path('login/', LoginView.as_view(template_name='login.html', authentication_form=views.CustomLoginForm), name='login'),
  path('logout/', LogoutView.as_view(next_page='dashboard'), name='logout'),
  path('register/', views.register, name='register'),
  path('forgot-password/', views.forgot_password, name='forgot_password'),
  path('set-language/', views.set_language, name='set_language'),
  path('switch-company/<int:company_id>/', views.switch_company, name='switch_company'),
]