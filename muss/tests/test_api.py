from rest_framework import status
from rest_framework.test import APITestCase


API_PREFIX = "/api/"


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

    def get_messages_forum(self):
        """
        Ensure we can get message forums
        """
        url = self.get_url_message_forum + "?forum=1"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def get_messages_forum_without_params(self):
        """
        Ensure we can get error 404 in endpoint without params
        """
        url = self.get_url_message_forum
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 404, True)
