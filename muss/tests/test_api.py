import io
import json
from PIL import Image

from django.conf import settings
from rest_framework.test import (
    APIRequestFactory, APITestCase, force_authenticate
)

from muss import utils as utils_muss
from muss.api import views
from muss.models import Register, Upload
from muss.tests import utils

API_PREFIX = "/api/"


class UserViewSetTests(APITestCase):

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

    def test_create_user_error(self):
        """
        Ensure we can create user with errors
        """
        url = self.get_url_users
        # Error validator
        response = self.client.post(url, {
            'last_name': 'Smith',
            'first_name': 'John',
        })
        self.assertEqual(response.status_code == 400, True)


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

    def test_check_permissions_forum_user_without_params_view(self):
        """
        Ensure we can get permissions user in forum
        """
        url = self.get_url_endpoint
        response = self.client.get(url)
        self.assertEqual(response.status_code == 404, True)


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

        up = Upload.objects.all().first()
        name_file = settings.MEDIA_ROOT + "/" + up.attachment.name
        utils_muss.remove_file(name_file)
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

    def test_create_hitcount_without_topic(self):
        """
        Ensure we display error
        """
        url = self.get_url_hitcounts
        response = self.client.post(url)
        self.assertEqual(response.status_code == 404, True)


class LikeTopicViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "liketopics/"

    def test_get_likes_topic(self):
        """
        Ensure we can get likes topic
        """
        url = self.get_url_endpoint
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_like_topic(self):
        """
        Ensure we can create like topic
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.LikeTopicViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'topic': str(topic.pk)
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 200, True)

    def test_create_like_topic_without_params(self):
        """
        Ensure we can create like topic without params
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.LikeTopicViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        request = factory.post(url)
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 404, True)

    def test_destroy_like_topic(self):
        """
        Ensure we can destroy like topic
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.LikeTopicViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })

        # Create
        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'topic': str(topic.pk)
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        # Delete
        url = self.get_url_endpoint + str(topic.pk) + "/"
        request = factory.delete(
            url, {
                'users': str(user.pk)
            }
        )
        force_authenticate(request, user=user)
        response = view(request, pk=topic.pk)

        self.assertEqual(response.status_code == 200, True)

    def test_destroy_like_topic_without_params(self):
        """
        Ensure we can destroy like topic without params
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.LikeTopicViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })

        # Create
        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'topic': str(topic.pk)
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        # Delete
        url = self.get_url_endpoint + str(topic.pk) + "/"
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, pk=topic.pk)

        self.assertEqual(response.status_code == 404, True)


class LikeCommentViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "likecomments/"

    def test_get_likes_comment(self):
        """
        Ensure we can get likes comment
        """
        url = self.get_url_endpoint
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_like_comment(self):
        """
        Ensure we can create like comment
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        comment = utils.create_comment(user)
        view = views.LikeCommentViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'comment': comment.pk
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 200, True)

    def test_create_like_comment_without_params(self):
        """
        Ensure we can create like comment without params
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.LikeCommentViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        request = factory.post(url)
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 404, True)

    def test_destroy_like_comment(self):
        """
        Ensure we can destroy like comment
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        comment = utils.create_comment(user)
        view = views.LikeCommentViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })

        # Create
        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'comment': comment.pk
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        # Delete
        url = self.get_url_endpoint + str(comment.pk) + "/"
        request = factory.delete(
            url, {
                'users': str(user.pk)
            }
        )
        force_authenticate(request, user=user)
        response = view(request, pk=comment.pk)

        self.assertEqual(response.status_code == 200, True)

    def test_destroy_like_comment_without_params(self):
        """
        Ensure we can destroy like comment without params
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        comment = utils.create_comment(user)
        view = views.LikeCommentViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })

        # Create
        url = self.get_url_endpoint
        request = factory.post(
            url, {
                'users': str(user.pk),
                'comment': comment.pk
            }
        )
        force_authenticate(request, user=user)
        response = view(request)

        # Delete
        url = self.get_url_endpoint + str(comment.pk) + "/"
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, pk=comment.pk)

        self.assertEqual(response.status_code == 404, True)


class CommentViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "comments/"

    def test_get_comments(self):
        """
        Ensure we can get comments
        """
        url = self.get_url_endpoint
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_comment(self):
        """
        Ensure we can get comment
        """
        user = utils.create_user()
        comment = utils.create_comment(user)
        url = self.get_url_endpoint + str(comment.pk) + "/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_comments_topic(self):
        """
        Ensure we can get comments topic
        """
        user = utils.create_user()
        topic = utils.create_topic(user)
        url = self.get_url_endpoint + "?=topic=" + str(topic.pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_comment(self):
        """
        Ensure we can create comment
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)

        view = views.CommentViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        self.data = {
            "data": {
                "attributes": {
                    "total_likes": None,
                    "date": None,
                    "description": "<p>Test create comment</p>",
                },
                "relationships": {
                    "user": {
                        "data": {
                            'id': str(user.pk),
                            'type': 'users'
                        }
                    },
                    "topic": {
                        "data": {
                            'id': str(topic.pk),
                            'type': 'topics'
                        }
                    }
                },
                "type": "comments"
            },
        }
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 201, True)

    def test_destroy_comment(self):
        """
        Ensure we can destroy comment
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        comment = utils.create_comment(user)
        view = views.CommentViewSet.as_view({
            'delete': 'destroy'
        })

        # Delete
        url = self.get_url_endpoint + str(comment.pk) + "/"
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, pk=comment.pk)

        self.assertEqual(response.status_code == 204, True)

    def test_update_comment(self):
        """
        Ensure we can update comment
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        comment = utils.create_comment(user)
        view = views.CommentViewSet.as_view({
            'patch': 'update'
        })

        # Update
        url = self.get_url_endpoint + str(comment.pk) + "/"

        self.data = {
            "data": {
                "attributes": {
                    "total_likes": comment.total_likes,
                    "date": None,
                    "description": "<p>Test create comment edited</p>",
                },
                "id": comment.pk,
                "relationships": {
                    "user": {
                        "data": {
                            'id': str(user.pk),
                            'type': 'users'
                        }
                    },
                    "topic": {
                        "data": {
                            'id': str(comment.topic.pk),
                            'type': 'topics'
                        }
                    }
                },
                "type": "comments"
            },
        }

        request = factory.patch(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request, pk=comment.pk)
        self.assertEqual(response.status_code == 200, True)


class RegisterViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "registers/"

    def go_to_endpoint(self, user, data):
        """
        Go to endpoint with method get
        """
        factory = APIRequestFactory()
        view = views.RegisterViewSet.as_view({
            'get': 'list'
        })

        url = self.get_url_endpoint
        request = factory.get(url, data)
        force_authenticate(request, user=user)
        response = view(request)
        return response

    def test_filter_get_registers(self):
        """
        Ensure we can get registers
        """
        user = utils.create_user()
        response = self.go_to_endpoint(user, {})
        self.assertEqual(response.status_code == 200, True)

    def test_filter_get_register(self):
        """
        Ensure we can filter get_register
        """
        user = utils.create_user()
        forum = utils.create_forum()
        response = self.go_to_endpoint(user, {
            'filter': 'get_register',
            'user': user.pk,
            'forum': forum.pk
        })
        self.assertEqual(response.status_code == 200, True)

    def test_filter_get_members(self):
        """
        Ensure we can filter members
        """
        user = utils.create_user()
        forum = utils.create_forum()
        response = self.go_to_endpoint(user, {
            'filter': 'members',
            'forum': forum.pk
        })
        self.assertEqual(response.status_code == 200, True)

    def test_destroy_register(self):
        """
        Ensure we can destroy register
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        register = utils.create_register(user)
        view = views.RegisterViewSet.as_view({
            'delete': 'destroy'
        })

        # Delete
        url = self.get_url_endpoint + str(register.pk) + "/"
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, pk=register.pk)

        self.assertEqual(response.status_code == 204, True)

    def test_create_register(self):
        """
        Ensure we can create register
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        forum = utils.create_forum()

        view = views.RegisterViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        self.data = {
            "data": {
                "attributes": {
                    "date": None,
                },
                "relationships": {
                    "user": {
                        "data": {
                            'id': str(user.pk),
                            'type': 'users'
                        }
                    },
                    "forum": {
                        "data": {
                            'id': str(forum.pk),
                            'type': 'forums'
                        }
                    }
                },
                "type": "registers"
            },
        }
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 201, True)


class TopicViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "topics/"

    def test_get_topics(self):
        """
        Ensure we can get topics
        """
        url = self.get_url_endpoint
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_topic(self):
        """
        Ensure we can get topic
        """
        user = utils.create_user()
        topic = utils.create_topic(user)
        url = self.get_url_endpoint + str(topic.pk) + "/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_get_topic_queryset(self):
        """
        Ensure we can get topic
        """
        user = utils.create_user()
        topic = utils.create_topic(user)
        forum = utils.create_forum()

        # Only topic
        url = self.get_url_endpoint
        url += "?=filter='only_topic'&topic=" + str(topic.pk)
        url += "&slug=" + topic.slug
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # By forum
        url = self.get_url_endpoint
        url += "?=filter='by_forum'&slug=" + forum.slug
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # Search
        url = self.get_url_endpoint
        url += "?=filter='search'&title='test'"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # By user
        url = self.get_url_endpoint
        url += "?=filter='by_user'&username=" + user.username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # Suggests
        url = self.get_url_endpoint
        url += "?=filter='suggests'&suggest='test'"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # Latest
        url = self.get_url_endpoint
        url += "?=filter='latest'"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_create_topic(self):
        """
        Ensure we can create topic
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        forum = utils.create_forum()
        view = views.TopicViewSet.as_view({
            'post': 'create'
        })

        # Create register
        Register.objects.create(forum=forum, user=user)

        url = self.get_url_endpoint
        self.data = utils.create_topic_data_api(user, forum)
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 201, True)

    def test_create_topic_not_register(self):
        """
        Ensure we can create topic not register in private forum
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        forum = utils.create_forum()
        view = views.TopicViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        self.data = utils.create_topic_data_api(user, forum)
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 403, True)

    def test_create_topic_public_forum(self):
        """
        Ensure we can create topic in public_forum
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        forum = utils.create_forum_public()
        view = views.TopicViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        self.data = utils.create_topic_data_api(user, forum)
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 201, True)

    def test_destroy_topic(self):
        """
        Ensure we can destroy topic
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.TopicViewSet.as_view({
            'delete': 'destroy'
        })

        # Delete
        url = self.get_url_endpoint + str(topic.pk) + "/"
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, pk=topic.pk)

        self.assertEqual(response.status_code == 204, True)

    def test_update_topic(self):
        """
        Ensure we can update topic
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.TopicViewSet.as_view({
            'patch': 'update'
        })

        # Update
        url = self.get_url_endpoint + str(topic.pk) + "/"

        self.data = {
            "data": {
                "attributes": {
                    "title": "Test topic",
                    "description": "<p>Test create topic edited</p>",
                },
                "id": topic.pk,
                "relationships": {
                    "user": {
                        "data": {
                            'id': str(user.pk),
                            'type': 'users'
                        }
                    },
                    "forum": {
                        "data": {
                            'id': str(topic.forum.pk),
                            'type': 'forums'
                        }
                    }
                },
                "type": "topics"
            },
        }

        request = factory.patch(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request, pk=topic.pk)
        self.assertEqual(response.status_code == 200, True)


class ProfileViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "profiles/"

    def test_filter_profiles(self):
        """
        Ensure we can get profiles
        """
        user = utils.create_user()
        url = self.get_url_endpoint

        # Get profiles
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

        # Get only profile
        response = self.client.get(url + str(user.user.pk), format='json')
        self.assertEqual(response.status_code == 200, True)

        # get_profile_username
        url += "?=filter='get_profile_username'&username=" + user.username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code == 200, True)

    def test_update_profile(self):
        """
        Ensure we can update profile
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        view = views.ProfileViewSet.as_view({
            'patch': 'update'
        })
        profile = user.user

        # Update
        url = self.get_url_endpoint + str(profile.pk) + "/"
        self.data = {
            "data": {
                "type": "profiles",
                "id": str(profile.pk),
                "attributes": {
                    "photo": "example.png",
                    "last-seen": "0 minutes",
                    "online": True,
                    "about": "Admin Test :)",
                    "location": "Buenos Aires, CABA, Argentina",
                    "activation-key": "86b58f8c2c832b8e135ee4afd4423aa",
                    "key-expires": "2017-11-23 03:14:27",
                    "is-troll": False,
                    "receive-emails": True
                },
                "relationships": {
                    "user": {
                        "data": {
                            "type": "User",
                            "id": str(user.pk)
                        }
                    }
                }
            }
        }

        request = factory.patch(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request, pk=profile.pk)
        self.assertEqual(response.status_code == 200, True)


class NotificationViewSetTests(APITestCase):

    @property
    def get_url_endpoint(self):
        """
        Get main url endpoint
        """
        return API_PREFIX + "notifications/"

    def test_get_notifications(self):
        """
        Ensure we can get notifications
        """
        factory = APIRequestFactory()
        url = self.get_url_endpoint
        user = utils.create_user()
        view = views.NotificationViewSet.as_view({
            'get': 'list'
        })
        url += "?user=" + str(user.pk)
        request = factory.get(url, format='json')

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code == 200, True)

    def test_get_notification(self):
        """
        Ensure we can get notification
        """
        factory = APIRequestFactory()
        url = self.get_url_endpoint
        user = utils.create_user()
        topic = utils.create_topic(user)
        notification = utils.create_notification(user, topic)
        view = views.NotificationViewSet.as_view({
            'get': 'list'
        })
        url += str(notification.pk) + "/?user=" + str(user.pk)
        request = factory.get(url, format='json')

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code == 200, True)

    def test_get_topic_queryset_limit(self):
        """
        Ensure we can get notifications limit
        """
        factory = APIRequestFactory()
        url = self.get_url_endpoint
        user = utils.create_user()
        topic = utils.create_topic(user)
        notification = utils.create_notification(user, topic)
        view = views.NotificationViewSet.as_view({
            'get': 'list'
        })
        url += str(notification.pk) + "/?user=" + str(user.pk) + "&limit=5"
        request = factory.get(url, format='json')

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code == 200, True)

    def test_create_notification(self):
        """
        Ensure we can create notification
        """
        factory = APIRequestFactory()
        user = utils.create_user()
        topic = utils.create_topic(user)
        view = views.NotificationViewSet.as_view({
            'post': 'create'
        })

        url = self.get_url_endpoint
        self.data = {
            "data": {
                "attributes": {
                    "is-seen": False,
                    "date": "2017-11-23 03:14:27"
                },
                "relationships": {
                    "user": {
                        "data": {
                            'id': str(user.pk),
                            'type': 'User'
                        }
                    },
                    "content-type": {
                        "data": {
                            'id': str(topic.pk),
                            'type': 'ContentType'
                        }
                    }
                },
                "type": "notifications"
            },
        }
        request = factory.post(
            url, json.dumps(self.data),
            HTTP_HOST='example.com', content_type="application/vnd.api+json"
        )
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code == 201, True)
