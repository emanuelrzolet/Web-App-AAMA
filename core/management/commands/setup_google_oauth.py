from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Setup Google OAuth configuration'

    def handle(self, *args, **options):
        # Delete all existing social apps
        SocialApp.objects.all().delete()
        self.stdout.write('Deleted existing social apps')

        # Get or create the default site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'localhost:8000', 'name': 'localhost'}
        )
        self.stdout.write(f'Using site: {site.domain}')

        # Get environment variables
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET')
            )
            return

        try:
            # Create new social app for Google
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=client_secret,
                key=''
            )
            app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Google OAuth app with ID: {app.id}')
            )
            
            # Verify the configuration
            apps = SocialApp.objects.filter(provider='google')
            self.stdout.write(f'Number of Google apps: {apps.count()}')
            for a in apps:
                self.stdout.write(f'App ID: {a.id}, Provider: {a.provider}, Name: {a.name}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}')) 