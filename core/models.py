from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from dateutil.relativedelta import relativedelta

# Create your models here.

class User(AbstractUser):
    telefone = models.CharField(max_length=20, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    estado_civil = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

class Endereco(models.Model):
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=8)

class FotoAnimal(models.Model):
    animal = models.ForeignKey('Animal', related_name='fotos_set', on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='animais/')
    is_principal = models.BooleanField(default=False)
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_principal', '-data_upload']

    def save(self, *args, **kwargs):
        if self.is_principal:
            # Se esta foto está sendo definida como principal, remove o status principal de outras fotos
            FotoAnimal.objects.filter(animal=self.animal, is_principal=True).update(is_principal=False)
        elif not FotoAnimal.objects.filter(animal=self.animal, is_principal=True).exists():
            # Se não existe foto principal, esta se torna a principal
            self.is_principal = True
        super().save(*args, **kwargs)

class Animal(models.Model):
    COMPORTAMENTO_CHOICES = [
        ('1', 'Dócil'),
        ('2', 'Agressivo'),
        ('3', 'Arisco'),
        ('4', 'Sociável'),
    ]
    
    PELAGEM_CHOICES = [
        ('1', 'Curta'),
        ('2', 'Média'),
        ('3', 'Longa'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    TIPO_CHOICES = [
        ('CACHORRO', 'Cachorro'),
        ('GATO', 'Gato'),
    ]

    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('ADOTADO', 'Adotado'),
    ]

    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    dataNascimento = models.DateField(null=True, blank=True)
    idadeEstimada = models.IntegerField(null=True, blank=True, help_text="Idade em anos")
    cor = models.CharField(max_length=50)
    comportamento = models.CharField(max_length=1, choices=COMPORTAMENTO_CHOICES)
    pelagem = models.CharField(max_length=1, choices=PELAGEM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    sexo_atual = models.BooleanField(default=True)
    genero = models.CharField(max_length=1, choices=SEXO_CHOICES)
    castrado = models.BooleanField(default=False)
    pertence_instituicao = models.BooleanField(default=True)
    entrada_instituicao = models.DateTimeField(auto_now_add=True)
    saida_instituicao = models.DateField(null=True, blank=True)

    @property
    def foto_principal(self):
        foto = self.fotos_set.filter(is_principal=True).first()
        if foto:
            return foto.foto
        return None

    def calcular_idade(self):
        if self.dataNascimento:
            hoje = date.today()
            idade = relativedelta(hoje, self.dataNascimento).years
            return idade
        return None

    def definir_data_nascimento(self):
        if not self.dataNascimento and self.idadeEstimada:
            hoje = date.today()
            self.dataNascimento = date(hoje.year - self.idadeEstimada, hoje.month, hoje.day)

    def clean(self):
        super().clean()
        # Se tiver data de nascimento, calcula a idade
        if self.dataNascimento:
            self.idadeEstimada = self.calcular_idade()
        # Se tiver idade estimada mas não tiver data de nascimento, define a data
        elif self.idadeEstimada and not self.dataNascimento:
            self.definir_data_nascimento()

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"

class Adocao(models.Model):
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    adotante = models.ForeignKey('User', on_delete=models.CASCADE)
    data_requisicao = models.DateTimeField(auto_now_add=True)

class Dose(models.Model):
    nome = models.CharField(max_length=255)
    data_aplicacao = models.DateField(auto_now_add=True)
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    vacina = models.ForeignKey('Vacinas', on_delete=models.CASCADE)

class Vacinas(models.Model):
    nome = models.CharField(max_length=255)

class RacaCachorro(models.Model):
    nome = models.CharField(max_length=50, default="SRD")

    def __str__(self):
        return self.nome

class Cachorro(models.Model):
    porte = models.IntegerField(choices=[(1, 'Pequeno'), (2, 'Médio'), (3, 'Grande')])
    raca = models.ForeignKey('RacaCachorro', on_delete=models.CASCADE)
    animal = models.OneToOneField('Animal', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.animal_id:
            raise ValidationError('É necessário criar um registro de Animal primeiro.')
        if self.animal.tipo != 'CACHORRO':
            raise ValidationError('O tipo do animal deve ser Cachorro.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal.nome} - {self.raca.nome}"

class RacaGato(models.Model):
    nome = models.CharField(max_length=50, default="SRD")

    def __str__(self):
        return self.nome

    @classmethod
    def get_default_raca(cls):
        raca, _ = cls.objects.get_or_create(nome="SRD")
        return raca.id

class Gato(models.Model):
    raca = models.ForeignKey('RacaGato', on_delete=models.CASCADE, default=RacaGato.get_default_raca)
    animal = models.OneToOneField('Animal', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.animal_id:
            raise ValidationError('É necessário criar um registro de Animal primeiro.')
        if self.animal.tipo != 'GATO':
            raise ValidationError('O tipo do animal deve ser Gato.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal.nome} - {self.raca.nome}"

@receiver(post_save, sender=Animal)
def create_animal_type(sender, instance, created, **kwargs):
    if created:
        if instance.tipo == 'CACHORRO':
            raca_default = RacaCachorro.objects.get_or_create(nome="SRD")[0]
            Cachorro.objects.create(animal=instance, raca=raca_default, porte=2)
        elif instance.tipo == 'GATO':
            raca_default = RacaGato.objects.get_or_create(nome="SRD")[0]
            Gato.objects.create(animal=instance, raca=raca_default)
