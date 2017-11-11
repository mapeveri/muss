from django.db.models import F
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

from muss.models import (
    Category, Comment, Forum, Profile,
    Notification, Topic, Register,
    Configuration
)
from muss.tests import utils


class CategoryTestCase(TestCase):
    """
    Test create/update/delete category
    """
    def test_create_update_delete_category(self):
        utils.create_category()

        Category.objects.filter(
            name="Backend"
        ).update(
            description="Backend category test"
        )

        Category.objects.filter(
            name="Backend"
        ).delete()


class ForumTestCase(TestCase):
    """
    Test create/update/delete forum
    """
    def setUp(self):
        utils.create_user()
        utils.create_category()

    def test_create_update_delete_forum(self):
        utils.create_forum()
        f = Forum.objects.filter(name="Django")
        f.update(
            description="Forum django framework"
        )
        f.delete()


class CreateTopicTestCase(TestCase):
    """
    Test create topic
    """
    def test_create_topic(self):
        user = utils.create_user()
        utils.create_topic(user)


class UpdateTopicTestCase(TestCase):
    """
    Test update topic
    """
    def setUp(self):
        utils.create_user()

    def test_update_topic(self):
        Topic.objects.filter(
            forum_id=1, user_id=1, pk=1
        ).update(description="Test topic update")


class DeleteTopicTestCase(TestCase):
    """
    Test delete topic
    """
    def setUp(self):
        utils.create_user()

    def test_delete_topic(self):
        Topic.objects.filter(
            forum_id=1, user_id=1, pk=1
        ).delete()


class NewCommentTopicTestCase(TestCase):
    """
    Test new comment
    """
    def test_new_comment(self):
        user = utils.create_user()
        topic = utils.create_topic(user)
        date = timezone.now()
        Comment.objects.create(
            topic=topic, user=user, date=date,
            description="Comment tests", total_likes=0
        )


class EditCommentTopicTestCase(TestCase):
    """
    Test edit comment
    """
    def setUp(self):
        utils.create_user()

    def test_edit_comment(self):
        Comment.objects.filter(
            topic_id=1, user_id=1, pk=1
        ).update(description="Comment test update")


class DeleteCommentTopicTestCase(TestCase):
    """
    Test delete comment
    """
    def setUp(self):
        utils.create_user()

    def test_delete_comment(self):
        Comment.objects.filter(
            topic_id=1, user_id=1, pk=1
        ).delete()


class NewNotificationTopicTestCase(TestCase):
    """
    Test new notification
    """
    def test_new_notification(self):
        user = utils.create_user()
        date = timezone.now()
        Notification.objects.create(
            id_object=1, user=user, date=date,
            is_seen=False
        )


class EditNotificationTopicTestCase(TestCase):
    """
    Test edit notification
    """
    def setUp(self):
        utils.create_user()

    def test_edit_notification(self):
        Notification.objects.filter(
            id_object=1, user_id=1
        ).update(is_seen=True)


class DeleteNotificationTopicTestCase(TestCase):
    """
    Test delete notification
    """
    def setUp(self):
        utils.create_user()

    def test_delete_notification(self):
        Notification.objects.filter(
            id_object=1, user_id=1
        ).delete()


class AddRegisterTestCase(TestCase):
    """
    Test add register to forum
    """
    def setUp(self):
        utils.create_user()
        utils.create_forum()

    def test_add_register_forum(self):
        User = get_user_model()
        user = User.objects.get(username="admin")
        Register.objects.create(
            user=user, date=timezone.now(), forum_id=1
        )


class UnRegisterTopicTestCase(TestCase):
    """
    Test Unregister to forum
    """
    def setUp(self):
        utils.create_user()
        utils.create_forum()

    def test_unregister_forum(self):
        Register.objects.filter(
            user_id=1, forum_id=1,
        ).delete()


class LikeTopicTestCase(TestCase):
    """
    Test like topic
    """
    def test_like_topic(self):
        Topic.objects.filter(pk=1).update(
            total_likes=F('total_likes') + 1
        )


class UnLikeTopicTestCase(TestCase):
    """
    Test Unlike topic
    """
    def test_unlike_topic(self):
        Topic.objects.filter(pk=1).update(
            total_likes=F('total_likes') - 1
        )


class IsTrollTestCase(TestCase):
    """
    Test Check user is troll
    """
    def test_is_troll(self):
        # Get troll
        user = utils.create_user()

        total = Forum.objects.filter(
            moderators=user
        ).count()

        # Check if is user correct
        if total == 0:
            # Is a troll
            Profile.objects.filter(
                user=user
            ).update(is_troll=True)


class EditProfileTestCase(TestCase):
    """
    Test Edit profile
    """
    def setUp(self):
        utils.create_user()

    def test_edit_profile(self):
        Profile.objects.filter(user_id=1).update(
            photo="", about="Example about", location="this.location",
            activation_key="", key_expires=timezone.now(),
            is_troll=False, receive_emails=True
        )


class ConfigurationTestCase(TestCase):
    """
    Test configuration
    """
    def test_configuration(self):
        mysite = Site.objects.get_current()
        mysite.domain = 'mysite.com'
        mysite.name = 'My Site'
        mysite.save()

        Configuration.objects.create(
            site=mysite, logo=None, favicon=None,
            logo_width=200, logo_height=200, custom_css="",
            description="Test", keywords="test, django"
        )
