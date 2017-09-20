from django.views.generic import TemplateView


class IndexView(TemplateView):
    """
    Index app
    """
    template_name = "muss/index.html"
