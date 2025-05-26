from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix social application configurations'

    def handle(self, *args, **options):
        # Get or create the default site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'localhost:8000', 'name': 'localhost'}
        )

        # Delete all existing social apps
        SocialApp.objects.all().delete()

        # Get environment variables
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR('Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment variables'))
            return

        # Create new social app for Google
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret
        )

        # Add the site to the social app
        google_app.sites.add(site)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully configured Google OAuth with client_id: {client_id}')
        ) 