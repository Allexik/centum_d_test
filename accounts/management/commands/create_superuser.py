from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

from django.db.models import Q


class Command(BaseCommand):
    help = 'Create a superuser using environment variables'

    def handle(self, *args, **kwargs):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(Q(username=username) | Q(email=email)).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" with email "{email}" created'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser with username "{username}" or email "{email}" already '
                                                 f'exists'))
