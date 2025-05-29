from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, AdotanteProfileForm, EnderecoFormSet


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Erro ao registrar. Por favor, corrija os erros abaixo.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/registration/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    try:
        adotante = user.adotante_profile
    except Exception:
        adotante = None

    if request.method == 'POST':
        adotante_form = AdotanteProfileForm(request.POST, instance=adotante)
        endereco_formset = EnderecoFormSet(request.POST, instance=adotante)
        if adotante_form.is_valid() and endereco_formset.is_valid():
            adotante = adotante_form.save(commit=False)
            adotante.user = user
            adotante.save()
            endereco_formset.instance = adotante
            endereco_formset.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        adotante_form = AdotanteProfileForm(instance=adotante)
        endereco_formset = EnderecoFormSet(instance=adotante)

    return render(request, 'core/profile.html', {
        'adotante_form': adotante_form,
        'endereco_formset': endereco_formset,
    })
