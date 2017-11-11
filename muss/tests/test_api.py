import io
from PIL import Image

from rest_framework.test import (
    APIRequestFactory, APITestCase, force_authenticate
)

from muss.api import views
from muss.tests import utils

API_PREFIX = "/api/"


class UsersViewSetTests(APITestCase):

    @property
    def get_url_users(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "users/"

    def test_get_users(self):
        """
        Ensure we can get users
        """
        url = self.get_url_users
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_only_user(self):
        """
        Ensure we can get only user
        """
        user = utils.create_user()
        url = self.get_url_users + str(user.pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_user(self):
        """
        Ensure we can create user
        """
        url = self.get_url_users
        response = self.client.post(url, {
            'last_name': 'Smith',
            'first_name': 'John',
            'username': 'john.smith',
            'email': 'john.smith@gmail.com',
            'password': '1234'
        })
        self.assertEqual(response.status_code == 201, True)


class CategoriesViewSetTests(APITestCase):

    @property
    def get_url_categories(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "categories/"

    def test_get_categories(self):
        """
        Ensure we can get categories
        """
        url = self.get_url_categories
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_categories_forums(self):
        """
        Ensure we can get categories and forums
        """
        url = self.get_url_categories + "?filter=forums"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)


class ForumsViewSetTests(APITestCase):

    @property
    def get_url_forums(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "forums/"

    def test_get_forums(self):
        """
        Ensure we can get forums
        """
        url = self.get_url_forums
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_only_forum(self):
        """
        Ensure we can get only forum
        """
        url = self.get_url_forums + "?filter=only&pk=1&slug=django"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)


class MessageForumViewSetTests(APITestCase):

    @property
    def get_url_message_forum(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "messageforums/"

    def test_get_messages_forum(self):
        """
        Ensure we can get message forums
        """
        url = self.get_url_message_forum + "?forum=1"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_messages_forum_without_params(self):
        """
        Ensure we can get error 404 in endpoint without params
        """
        url = self.get_url_message_forum
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 404, True)


class UpdateSeenNotificationsTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "update-seen-notifications-user/"

    def test_update_seen_notifications_user_without_login(self):
        """
        Ensure we can get error 404 in endpoint witout login
        """
        url = self.get_url_endpoint
        response = self.client.post(url, {'user_id': 1})
        self.assertEqual(response.status_code == 404, True)

    def test_update_seen_notifications_user_with_login(self):
        """
        Ensure we can get error 200 in endpoint with login
        for update notifications seen user.
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.UpdateSeenNotifications.as_view()

        url = self.get_url_endpoint
        request = factory.post(url, {'user_id': user.id})
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code == 200, True)


class GetTotalPendingNotificationsUserTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "get-total-pending-notifications-user/"

    def test_get_total_pending_notifications_user_without_login(self):
        """
        Ensure we can get error 404 in endpoint witout login
        """
        url = self.get_url_endpoint
        response = self.client.get(url, {'user_id': 1})
        self.assertEqual(response.status_code == 404, True)

    def test_get_total_pending_notifications_user_with_login(self):
        """
        Ensure we can get error 404 in endpoint with login
        for get total notifications for user
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.GetTotalPendingNotificationsUser.as_view()

        url = self.get_url_endpoint
        request = factory.get(url, {'user_id': user.id})
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code == 200, True)


class CheckPermissionsForumUserViewTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "check-permissions-forum-user/"

    def test_check_permissions_forum_user_view(self):
        """
        Ensure we can get permissions user in forum
        """
        url = self.get_url_endpoint
        response = self.client.get(url, {'user_id': 1, 'forum_id': 1})
        self.assertEqual(response.status_code == 200, True)


class UploadsViewTests(APITestCase):

    fixtures = []
    maxDiff = None

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "uploads/"

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_uploads_view(self):
        """
        Ensure we can uploads files
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.UploadsView.as_view()

        url = self.get_url_endpoint
        photo_file = self.generate_photo_file()
        data = {
            'photo': photo_file,
        }

        request = factory.post(
            url, data, HTTP_HOST='example.com', format='multipart'
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 200, True)


class HitcountTopicViewSetTests(APITestCase):

    @property
    def get_url_hitcounts(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "hitcounts/"

    def test_get_hitcounts(self):
        """
        Ensure we can get hitcounts
        """
        url = self.get_url_hitcounts
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_hitcount(self):
        """
        Ensure we can create hitcount
        """
        url = self.get_url_hitcounts
        user = utils.create_user()
        topic = utils.create_topic(user)
        response = self.client.post(url, {"topic": topic.pk})
        self.assertEqual(response.status_code == 200, True)
