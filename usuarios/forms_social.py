from allauth.socialaccount.forms import SignupForm

class SocialSignupForm(SignupForm):
    def save(self, request):
        # Apenas cria o usuário, dados extras do perfil serão preenchidos depois
        user = super().save(request)
        return user
