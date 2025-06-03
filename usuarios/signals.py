from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import AdotanteProfile, User

@receiver(user_signed_up)
def create_adotante_profile_on_social_signup(request, user, **kwargs):
    # Cria o perfil apenas se não existir
    if not hasattr(user, 'adotante_profile'):
        AdotanteProfile.objects.create(user=user)
