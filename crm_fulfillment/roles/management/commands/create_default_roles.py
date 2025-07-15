from django.core.management.base import BaseCommand
from django.utils.text import slugify
from roles.models import Role, Permission

class Command(BaseCommand):
    help = "Creates default roles and permissions for the system"

    def handle(self, *args, **options):
        self.stdout.write("Creating default roles and permissions...")
