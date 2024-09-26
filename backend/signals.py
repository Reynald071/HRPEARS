from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver

from backend.models import DjangoLoggedInUser


@receiver(user_logged_in)
def on_user_logged_in(sender, **kwargs):
    DjangoLoggedInUser.objects.get_or_create(user=kwargs.get('user'))


@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    DjangoLoggedInUser.objects.filter(user=kwargs.get('user')).delete()
