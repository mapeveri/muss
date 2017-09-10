from rest_framework.renderers import JSONRenderer


class JSONRendererApiJson(JSONRenderer):
    """
    Render a JSON response per the JSON API spec:
    """
    media_type = 'application/vnd.api+json'
    format = 'vnd.api+json'
