from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates the default groups'

    def handle(self, *args, **kwargs):
        admin_group, created = Group.objects.get_or_create(name='Admin')
        basic_user_group, created = Group.objects.get_or_create(name='Basic User')

        self.stdout.write(self.style.SUCCESS('Successfully created groups'))
