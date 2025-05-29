from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, AdotanteProfile, Endereco

class AdotanteProfileForm(forms.ModelForm):
    class Meta:
        model = AdotanteProfile
        fields = ['telefone', 'profissao', 'estado_civil', 'cpf']

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        # Validação simplificada, pode ser expandida
        return cpf

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['bairro', 'logradouro', 'numero', 'complemento', 'cep']

EnderecoFormSet = forms.inlineformset_factory(
    AdotanteProfile, Endereco, form=EnderecoForm,
    fields=['bairro', 'logradouro', 'numero', 'complemento', 'cep'],
    extra=1, can_delete=True
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
