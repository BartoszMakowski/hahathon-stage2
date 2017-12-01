from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

ADMIN_USERNAME = 'GameAdmin'
ADMIN_EMAIL = 'hahaton@venturedevs.com'
ADMIN_PASSWORD = 'VdHahaton23!'


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            admin = user_model.objects.get(username=ADMIN_USERNAME,
                                           email=ADMIN_EMAIL)
            admin.set_password(ADMIN_PASSWORD)
            admin.save()
        except user_model.DoesNotExist:
            user_model.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL,
                                                ADMIN_PASSWORD)
