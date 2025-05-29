from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    telefone = models.CharField(max_length=20, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    estado_civil = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
