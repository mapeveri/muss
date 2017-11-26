from django import forms
from django.contrib.staticfiles import finders

from muss import models, widgets


class FormAdminTopic(forms.ModelForm):
    """
    Form for topic cadmin.
    """
    class Meta:
        model = models.Topic
        exclude = ('slug', 'id_attachment')
        widgets = {
            'description': widgets.TextareaWidget,
        }


class FormAdminProfile(forms.ModelForm):
    """
    Form for admin profile.
    """
    class Meta:
        model = models.Profile
        exclude = (
            'user',
        )
        widgets = {
            'about': widgets.TextareaWidget,
        }


class FormAdminConfiguration(forms.ModelForm):
    """
    Form configuration.

    - **parameters**:
        :param name_file_custom: Custom css file for the configuration.
    """
    name_file_custom = finders.find('css/custom.css')

    class Meta:
        model = models.Configuration
        exclude = (
            'pk',
        )

    def __init__(self, *args, **kwargs):
        # Read css custom
        file_custom = open(self.name_file_custom, 'r')
        file_custom = file_custom.read()

        # Override init value on edit
        initial = kwargs.get('initial', {})
        initial['custom_css'] = file_custom
        kwargs['initial'] = initial
        super(FormAdminConfiguration, self).__init__(*args, **kwargs)

        # Init value to new record
        self.fields['custom_css'].initial = file_custom

    def save(self, commit=True):
        instance = super(FormAdminConfiguration, self).save(commit=False)

        # Save content in the file
        with open(self.name_file_custom, "w") as text_file:
            text_file.write(instance.custom_css)

        if commit:
            instance.save()
        return instance
