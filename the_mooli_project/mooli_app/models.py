from django.contrib.auth.models import AbstractUser
from django.db import models

# Models appear here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Company(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    default_language = models.CharField(max_length=10, default='en')
    def __str__(self):
        return f"{self.user.email}'s Profile"