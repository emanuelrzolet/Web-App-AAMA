from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Animal, Cachorro, Gato, RacaCachorro, RacaGato

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    telefone = forms.CharField(required=True, label='Telefone')
    profissao = forms.CharField(required=False, label='Profissão')
    estado_civil = forms.ChoiceField(
        required=False,
        label='Estado Civil',
        choices=[
            ('', 'Selecione...'),
            ('SOLTEIRO', 'Solteiro(a)'),
            ('CASADO', 'Casado(a)'),
            ('DIVORCIADO', 'Divorciado(a)'),
            ('VIUVO', 'Viúvo(a)'),
        ]
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'telefone',
            'profissao', 'estado_civil'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class AnimalTypeForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=Animal.TIPO_CHOICES,
        label="Tipo de Animal",
        widget=forms.RadioSelect
    )

class CachorroForm(forms.ModelForm):
    class Meta:
        model = Cachorro
        fields = ['porte', 'raca']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['raca'].queryset = RacaCachorro.objects.all().order_by('nome')

class GatoForm(forms.ModelForm):
    class Meta:
        model = Gato
        fields = ['raca']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['raca'].queryset = RacaGato.objects.all().order_by('nome')

class AnimalForm(forms.ModelForm):
    # Add type-specific fields
    raca_cachorro = forms.ModelChoiceField(
        queryset=RacaCachorro.objects.all().order_by('nome'),
        required=False,
        label='Raça',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    raca_gato = forms.ModelChoiceField(
        queryset=RacaGato.objects.all().order_by('nome'),
        required=False,
        label='Raça',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    porte = forms.ChoiceField(
        choices=[
            (1, 'Pequeno'),
            (2, 'Médio'),
            (3, 'Grande')
        ],
        required=False,
        label='Porte',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Animal
        exclude = ['entrada_instituicao']
        widgets = {
            'dataNascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'comportamento': forms.Select(attrs={'class': 'form-control'}),
            'pelagem': forms.Select(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize type-specific fields
        self.fields['raca_cachorro'].queryset = RacaCachorro.objects.all().order_by('nome')
        self.fields['raca_gato'].queryset = RacaGato.objects.all().order_by('nome')
        
        if self.instance and self.instance.pk:
            self.fields['tipo'].disabled = True
            # Set initial values for type-specific fields
            if hasattr(self.instance, 'cachorro'):
                self.fields['raca_cachorro'].initial = self.instance.cachorro.raca
                self.fields['porte'].initial = self.instance.cachorro.porte
            elif hasattr(self.instance, 'gato'):
                self.fields['raca_gato'].initial = self.instance.gato.raca

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == 'CACHORRO':
            if not cleaned_data.get('raca_cachorro'):
                self.add_error('raca_cachorro', 'Este campo é obrigatório para cachorros.')
            if not cleaned_data.get('porte'):
                self.add_error('porte', 'Este campo é obrigatório para cachorros.')
        elif tipo == 'GATO':
            if not cleaned_data.get('raca_gato'):
                self.add_error('raca_gato', 'Este campo é obrigatório para gatos.')

        return cleaned_data 