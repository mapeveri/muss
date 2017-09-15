from django.conf import settings

from .models import Configuration


def data_templates(request):
    """
    context_processors for get in all templates.
    """
    # Get configurations
    try:
        configurations = Configuration.objects.all()[:1].get()
    except Configuration.DoesNotExist:
        configurations = None

    return {
        'SETTINGS': settings,
        'configurations': configurations
    }