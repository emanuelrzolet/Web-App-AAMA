# core/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.conf import settings # Importar settings para referenciar AUTH_USER_MODEL

# Create your models here.

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

class DisponiveisManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='DISPONIVEL')

class Animal(models.Model):
    COMPORTAMENTO_CHOICES = [
        ('1', 'Dócil'),
        ('2', 'Agressivo'),
        ('3', 'Arisco'),
        ('4', 'Sociável'),
    ]
    
    COR_CHOICES = [
        ('PRETO', 'Preto'),
        ('BRANCO', 'Branco'),
        ('MARROM', 'Marrom'),
        ('CINZA', 'Cinza'),
        ('CARAMELO', 'Caramelo'),
        ('MESCLADO', 'Mesclado'),
        ('OUTRO', 'Outro'),
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
    cor = models.CharField(max_length=50, choices=COR_CHOICES, null=True, blank=True)
    comportamento = models.CharField(max_length=1, choices=COMPORTAMENTO_CHOICES)
    pelagem = models.CharField(max_length=1, choices=PELAGEM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    genero = models.CharField(max_length=1, choices=SEXO_CHOICES)
    castrado = models.BooleanField(default=False)
    pertence_instituicao = models.BooleanField(default=True)
    entrada_instituicao = models.DateTimeField(default=timezone.now)
    saida_instituicao = models.DateField(null=True, blank=True)
    descricao = models.TextField(null=True, blank=True, help_text="Descrição sobre o animal, seu comportamento, história, etc.")

    # Campo para ligar o animal ao usuário que o cadastrou/é responsável
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Referencia o modelo de usuário definido em settings.py
        on_delete=models.SET_NULL, # Define o campo como NULL se o usuário for deletado
        null=True, # Permite que o campo seja NULL no banco de dados
        blank=True, # Permite que o campo seja opcional no formulário
        related_name='animais_cadastrados', # Nome reverso para acessar animais de um usuário
        help_text="Usuário responsável pelo cadastro deste animal."
    )

    # Manager customizado: Animal.disponiveis.all() retorna apenas disponíveis
    objects = models.Manager()  # Manager padrão
    disponiveis = DisponiveisManager()  # Manager para disponíveis

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def foto_principal(self):
        foto = self.fotos_set.filter(is_principal=True).first()
        if foto:
            return foto.foto
        return None

    @property
    def foto_url(self): # Adicionada para facilitar o acesso à URL da foto no template
        principal_foto = self.fotos_set.filter(is_principal=True).first()
        if principal_foto and principal_foto.foto:
            return principal_foto.foto.url
        return settings.STATIC_URL + 'images/no-photo.png' # Assumindo uma imagem padrão

    def calcular_idade(self):
        if self.dataNascimento:
            hoje = date.today()
            idade = relativedelta(hoje, self.dataNascimento).years
            return idade
        return None

    def definir_data_nascimento(self):
        if not self.dataNascimento and self.idadeEstimada is not None:
            hoje = date.today()
            self.dataNascimento = date(hoje.year - self.idadeEstimada, hoje.month, hoje.day)

    def clean(self):
        super().clean()
        if self.dataNascimento:
            self.idadeEstimada = self.calcular_idade()
        elif self.idadeEstimada is not None and not self.dataNascimento:
            self.definir_data_nascimento()
        

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        ordering = ['-entrada_instituicao'] # Ordena os animais pelos mais recentes primeiro

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Referencia o modelo de usuário
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure each user can only like an animal once
        unique_together = ('user', 'animal')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f"{self.user.username} likes {self.animal.nome}"

class Dose(models.Model):
    nome = models.CharField(max_length=255)
    data_aplicacao = models.DateField(auto_now_add=True)
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    vacina = models.ForeignKey('Vacinas', on_delete=models.CASCADE)

class Vacinas(models.Model):
    nome = models.CharField(max_length=255)

class RacaCachorro(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

    @classmethod
    def get_default_raca(cls):
        raca, created = cls.objects.get_or_create(nome="Sem raça definida")
        return raca

    @classmethod
    def get_default_raca_id(cls):
        return cls.get_default_raca().id

    class Meta:
        verbose_name = 'Raça de Cachorro'
        verbose_name_plural = 'Raças de Cachorro'
        ordering = ['nome']
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

    @classmethod
    def get_default_raca(cls):
        raca, created = cls.objects.get_or_create(nome="Sem raça definida") # Alterado para "Sem raça definida" para consistência com o sinal
        return raca

    class Meta:
        verbose_name = 'Raça de Cachorro'
        verbose_name_plural = 'Raças de Cachorro'
        ordering = ['nome']

class Cachorro(models.Model):
    porte = models.IntegerField(choices=[(1, 'Pequeno'), (2, 'Médio'), (3, 'Grande')])
    raca = models.ForeignKey('RacaCachorro', on_delete=models.SET_NULL, null=True)
 # Usa SET_NULL
    animal = models.OneToOneField('Animal', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.animal_id:
            raise ValidationError('É necessário criar um registro de Animal primeiro.')
        if self.animal.tipo != 'CACHORRO':
            raise ValidationError('O tipo do animal deve ser Cachorro.')
        # A raça padrão agora é tratada pelo 'default' no campo ForeignKey
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal.nome} - {self.raca.nome}"

class RacaGato(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

    @classmethod
    def get_default_raca(cls):
        raca, created = cls.objects.get_or_create(nome="Sem raça definida") # Alterado para "Sem raça definida" para consistência com o sinal
        return raca

    @classmethod
    def get_default_raca_id(cls):
        return cls.get_default_raca().id

    class Meta:
        verbose_name = 'Raça de Gato'
        verbose_name_plural = 'Raças de Gato'
        ordering = ['nome']

class Gato(models.Model):
    raca = models.ForeignKey('RacaGato', on_delete=models.SET_NULL, null=True) # Usa SET_NULL
    animal = models.OneToOneField('Animal', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.animal_id:
            raise ValidationError('É necessário criar um registro de Animal primeiro.')
        if self.animal.tipo != 'GATO':
            raise ValidationError('O tipo do animal deve ser Gato.')
        # A raça padrão agora é tratada pelo 'default' no campo ForeignKey
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal.nome} - {self.raca.nome}"

@receiver(post_save, sender=Animal)
def create_animal_type(sender, instance, created, **kwargs):
    if created:
        if instance.tipo == 'CACHORRO':
            raca_default = RacaCachorro.objects.get_or_create(nome="Sem raça definida")[0]
            # O porte default 2 (Médio) foi mantido.
            Cachorro.objects.create(animal=instance, raca=raca_default, porte=2)
        elif instance.tipo == 'GATO':
            raca_default = RacaGato.objects.get_or_create(nome="Sem raça definida")[0]
            Gato.objects.create(animal=instance, raca=raca_default)