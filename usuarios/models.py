from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

class AdotanteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adotante_profile')
    telefone = models.CharField(max_length=20)
    profissao = models.CharField(max_length=100)
    estado_civil = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Adotante: {self.user.username} ({self.cpf})"

class Endereco(models.Model):
    adotante = models.ForeignKey(AdotanteProfile, on_delete=models.CASCADE, related_name='enderecos')
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro} ({self.cep})"
