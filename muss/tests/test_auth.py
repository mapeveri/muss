from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone

from muss.tests import utils


class LoginTestCase(TestCase):
    """
    Check login url
    """
    def setUp(self):
        utils.create_user()

    def test_login(self):
        c = Client()
        response = c.post(reverse_lazy("token_auth"), {
            'username': 'admin', 'password': 'admin123456'
        })
        self.assertTrue(
            response.status_code == 302 or response.status_code == 200
        )


class LogoutTestCase(TestCase):
    """
    Check logout
    """
    def setUp(self):
        utils.create_user()

    def test_logout(self):
        c = Client()
        r = c.login(username='admin', password='admin123456')
        self.assertTrue(r)
        r = c.logout()


class SignupTestCase(TestCase):
    """
    Check signup url
    """
    def test_signup(self):
        now = timezone.now()

        # Create user
        User = get_user_model()
        us = User(
            username="user", email="user@musette.com",
            first_name="User",
            last_name="Musette", is_active=False,
            is_superuser=False, date_joined=now,
            is_staff=False
        )
        us.set_password("user123456")
        us.save()
