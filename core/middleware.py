from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class PerfilCompletoRequiredMiddleware:
    """
    Redireciona usuários autenticados para a página de perfil se o perfil estiver incompleto.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Evita loop infinito
            if request.path not in [reverse('profile'), reverse('account_logout')]:
                try:
                    perfil = request.user.adotante_profile
                    campos_obrigatorios = [perfil.telefone, perfil.profissao, perfil.estado_civil, perfil.cpf]
                    if not all(campos_obrigatorios):
                        return redirect('profile')
                except Exception:
                    return redirect('profile')
        return self.get_response(request)
