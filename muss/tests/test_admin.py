from django.test import TestCase
from django.contrib.sites.models import Site

from muss import forms
from muss.tests import utils


class ConfigurationModelAdminTests(TestCase):
    def test_configuration_form_admin(self, *args, **kwargs):
        """
        Test form configuration
        """
        mysite = Site.objects.create(domain='mysite.com', name="My Site")
        form = forms.FormAdminConfiguration({
            'site': mysite.pk,
            'logo': '',
            'favicon': '',
            'logo_width': 100,
            'logo_height': 100,
            'custom_css': '.cl { color: red }',
            'description': 'Test',
            'keywords': 'tests, test',
        })
        self.assertTrue(form.is_valid())


class ProfileModelAdminTests(TestCase):
    def test_profile_form_admin(self, *args, **kwargs):
        """
        Test form profile
        """
        user = utils.create_user()
        form = forms.FormAdminProfile({
            'user': user.pk,
            'about': 'Test profile',
            'location': 'Location test',
            'receive_email': True,
            'activation_key': 'xxxxxx',
            'key_expires': "2017-11-23 03:14:27",
        })
        self.assertTrue(form.is_valid())
