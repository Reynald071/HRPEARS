from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'
    verbose_name = 'libraries'

    def ready(self):
        import backend.signals
