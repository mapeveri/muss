from django import forms
from django.contrib.staticfiles.templatetags.staticfiles import static


class TextareaWidget(forms.Textarea):
    """
    Widget rich textarea.
    """
    class Media:
        # Simplemde
        js = (
            'https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js',
            static('js/textareas.js'),
        )
        css = {
            'all': (
                'https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css',
                static('css/custom_editor.css'),
            )
        }
