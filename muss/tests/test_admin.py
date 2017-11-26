from django.test import TestCase
from django.contrib.sites.models import Site

from muss import forms
from muss.tests import utils


class ConfigurationModelAdminTests(TestCase):
    def test_configuration_form_admin_true(self, *args, **kwargs):
        """
        Test form admin configuration
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

    def test_configuration_form_admin_false(self, *args, **kwargs):
        """
        Test form admin configuration
        """
        form = forms.FormAdminConfiguration({
            'site': None,
            'logo': '',
            'favicon': '',
            'logo_width': 100,
            'logo_height': 100,
            'custom_css': '.cl { color: red }',
            'description': 'Test',
            'keywords': 'tests, test',
        })
        self.assertFalse(form.is_valid())


class ProfileModelAdminTests(TestCase):
    def test_profile_form_admin_true(self, *args, **kwargs):
        """
        Test form admin profile
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

    def test_profile_form_admin_false(self, *args, **kwargs):
        """
        Test form admin profile
        """
        user = utils.create_user()
        form = forms.FormAdminProfile({
            'user': user.pk,
            'about': 'Test profile',
            'location': 'Location test',
            'receive_email': True,
            'activation_key': '',
            'key_expires': '',
        })
        self.assertFalse(form.is_valid())


class TopicAdminTests(TestCase):
    def test_topic_form_admin_true(self, *args, **kwargs):
        """
        Test form admin topic
        """
        user = utils.create_user()
        forum = utils.create_forum()
        form = forms.FormAdminTopic({
            'user': user.pk,
            'forum': forum.pk,
            'title': 'Test topic',
            'description': 'Test description',
            'photo': '',
            'is_close': False,
            'is_moderate': True,
            'is_top':  False,
        })
        self.assertTrue(form.is_valid())

    def test_topic_form_admin_false(self, *args, **kwargs):
        """
        Test form admin topic
        """
        user = utils.create_user()
        forum = utils.create_forum()
        form = forms.FormAdminTopic({
            'user': user.pk,
            'forum': forum.pk,
            'title': 'Test topic',
            'description': '',
            'photo': '',
            'is_close': False,
            'is_moderate': True,
            'is_top':  False,
        })
        self.assertFalse(form.is_valid())
