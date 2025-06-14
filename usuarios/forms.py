from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import User, AdotanteProfile, Endereco

class AdotanteProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', required=True)
    last_name = forms.CharField(label='Sobrenome', required=True)

    class Meta:
        model = AdotanteProfile
        fields = ['first_name', 'last_name', 'telefone', 'profissao', 'estado_civil', 'cpf']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        elif user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user if profile.user_id else self.initial.get('user')
        if not user and hasattr(self, 'user'):
            user = self.user
        if not user:
            raise ValueError('Usuário não encontrado para salvar nome.')
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        profile.user = user
        if commit:
            profile.save()
        return profile

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        # Validação simplificada, pode ser expandida
        return cpf

class EnderecoForm(forms.ModelForm): # BaseEnderecoFormSet removed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the form is bound (i.e., has data) and the delete checkbox for this form was checked in the POST data
        if self.is_bound and self.data.get(f'{self.prefix}-DELETE'):
            for field_name, field in self.fields.items():
                field.required = False

    class Meta:
        model = Endereco
        fields = ['bairro', 'logradouro', 'numero', 'complemento', 'cep']

EnderecoFormSet = forms.inlineformset_factory(
    AdotanteProfile, Endereco, form=EnderecoForm,
    fields=['bairro', 'logradouro', 'numero', 'complemento', 'cep'],
    extra=1, max_num=1, can_delete=False, validate_max=True
)


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
