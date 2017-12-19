from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from muss.tests import utils


class ConfigAdminTest(TestCase):
    def test_command_output(self):
        """
        Test command config_admin
        """
        out = StringIO()
        call_command('config_admin', stdout=out)
        self.assertIn('Finished work.', out.getvalue())


class CreateProfileSuperAdminTest(TestCase):
    def test_command_output(self):
        """
        Test command create_profile_superadmin
        """
        out = StringIO()
        utils.create_superuser()
        call_command('create_profile_superadmin', stdout=out)
        self.assertIn('Finished.', out.getvalue())
