from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, AdotanteProfileForm, EnderecoFormSet
from .models import AdotanteProfile  # Importar AdotanteProfile


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
    except AdotanteProfile.DoesNotExist:
        adotante = None

    if request.method == 'POST':
        adotante_form = AdotanteProfileForm(request.POST, instance=adotante, user=user)
        endereco_formset = EnderecoFormSet(request.POST, instance=adotante)
        print('[DEBUG] adotante_form errors:', adotante_form.errors)
        print('[DEBUG] endereco_formset errors:', endereco_formset.errors)
        if adotante_form.is_valid() and endereco_formset.is_valid():
            adotante_instance = adotante_form.save(commit=False)
            if not adotante_instance.pk: # Se é uma nova instância (sem pk)
                adotante_instance.user = user
            adotante_instance.save()
            adotante = adotante_instance # Atualiza a referência para a instância salva
            endereco_formset.instance = adotante # Usa a instância de adotante (nova ou atualizada)
            endereco_formset.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            next_url = request.POST.get('next') or request.GET.get('next')
            print('[DEBUG] Valor de next_url ao salvar perfil:', next_url)
            if next_url:
                return redirect(next_url)
            return redirect('usuarios:profile') # Usar namespace
        # Se não for válido, mantém o next do POST ou GET
        next_url = request.POST.get('next') or request.GET.get('next')
    else:
        adotante_form = AdotanteProfileForm(instance=adotante, user=user)
        endereco_formset = EnderecoFormSet(instance=adotante)
        next_url = request.GET.get('next')

    # Importação adiada para evitar import circular
    from adocao.models import Adocao
    solicitacoes_doacao = Adocao.objects.filter(usuario=user)

    context = {
        'adotante_form': adotante_form,
        'endereco_formset': endereco_formset,
        'solicitacoes_doacao': solicitacoes_doacao,
    }
    if next_url:
        context['next'] = next_url
    return render(request, 'profile.html', context)

