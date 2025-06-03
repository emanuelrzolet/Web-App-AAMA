from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.models import Animal
from usuarios.models import AdotanteProfile # Adicionado para verificar o perfil
from .models import Adocao
import json

@require_POST
@login_required
def criar_adocao(request):
    # Verificar se o perfil do adotante está completo
    try:
        profile = request.user.adotante_profile
        if not all([profile.telefone, profile.profissao, profile.estado_civil, profile.cpf, profile.enderecos.exists()]) :
            return JsonResponse({
                'success': False, 
                'error': 'Para se candidatar é necessário preencher os dados no perfil.',
                'redirect_url': reverse('usuarios:profile') 
            })
    except AdotanteProfile.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Para se candidatar é necessário preencher os dados no perfil.',
            'redirect_url': reverse('usuarios:profile')
        })

    data = json.loads(request.body)
    animal_id = data.get('animal_id')
    try:
        animal = Animal.objects.get(pk=animal_id, status='DISPONIVEL')
        adocao, created = Adocao.objects.get_or_create(animal=animal, usuario=request.user, confirmado=False)
        if not created:
            return JsonResponse({'success': False, 'error': 'Você já solicitou adoção para este animal.'})
        return JsonResponse({'success': True})
    except Animal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Animal não encontrado ou já adotado.'})
