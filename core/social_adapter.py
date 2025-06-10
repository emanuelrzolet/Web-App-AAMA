from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        next_url = (
            request.GET.get('next')
            or request.POST.get('next')
            or request.session.get('next')
        )
        print("DEBUG SOCIAL LOGIN REDIRECT:", next_url, dict(request.GET), dict(request.POST), dict(request.session))
        if next_url:
            return next_url
        return super().get_login_redirect_url(request)
