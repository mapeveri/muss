from django.apps import AppConfig


class mussConfig(AppConfig):
    """
    muss app configuration.
    """
    name = 'muss'

    def ready(self):
        # Import signals
        import muss.signals
