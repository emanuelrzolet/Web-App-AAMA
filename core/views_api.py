from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def tem_perfil_adotante(request):
    user = request.user
    tem_perfil = hasattr(user, 'adotante_profile')
    return JsonResponse({'tem_perfil': tem_perfil})
