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

class AnimalForm(forms.ModelForm):
    cor = forms.CharField(
        required=False,
        widget=forms.Select(
            choices=[('', '---------')] + Animal.COR_CHOICES,
            attrs={'class': 'form-control'}
        )
    )
    raca_cachorro = forms.ModelChoiceField(
        queryset=RacaCachorro.objects.all(),
        required=False,
        empty_label=None
    )
    raca_gato = forms.ModelChoiceField(
        queryset=RacaGato.objects.all(),
        required=False,
        empty_label=None
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
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={'class': 'tipo-select'}),
            'dataNascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comportamento': forms.Select(attrs={'class': 'form-control'}),
            'pelagem': forms.Select(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for races
        try:
            self.fields['raca_cachorro'].initial = RacaCachorro.get_default_raca().id
        except:
            pass
        try:
            self.fields['raca_gato'].initial = RacaGato.get_default_raca().id
        except:
            pass
        
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

class CachorroForm(forms.ModelForm):
    class Meta:
        model = Cachorro
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['raca'].initial = RacaCachorro.get_default_raca()
        except:
            pass
        self.fields['raca'].empty_label = None

class GatoForm(forms.ModelForm):
    class Meta:
        model = Gato
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['raca'].initial = RacaGato.get_default_raca()
        except:
            pass
        self.fields['raca'].empty_label = None 