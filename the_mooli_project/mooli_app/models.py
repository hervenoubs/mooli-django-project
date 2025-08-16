from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # Add first_name and last_name as required

class Company(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    companies = models.ManyToManyField(Company, related_name='user_profiles')  # Multiple companies
    current_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='current_user_profiles')  # Current active company
    default_language = models.CharField(max_length=10, default='en')
    activation_key = models.CharField(max_length=40, blank=True, null=True)  # For activation
    activation_expiry = models.DateTimeField(blank=True, null=True)  # For expiry
    
    def __str__(self):
        return f"{self.user.email}'s Profile"