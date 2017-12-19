from django.contrib.auth import get_user_model
from django.utils import timezone

from muss.models import (
    Category, Comment, Forum,
    Notification, Register, Topic
)


def create_user():
    """
    Create user in table
    """
    username = "admin"
    email = "admin@admin.com"
    password = "admin123456"
    User = get_user_model()
    user = User.objects.create_user(
        username, email, password
    )
    user.save()
    return user


def create_superuser():
    """
    Create user in table
    """
    username = "admin"
    email = "admin@admin.com"
    password = "admin123456"
    User = get_user_model()
    user = User.objects.create(
        username=username, email=email, is_superuser=True
    )
    user.set_password(password)
    user.save()
    return user


def create_category():
    category = Category.objects.create(
        name="Backend", description="Backend category"
    )
    return category


def create_forum():
    category = create_category()
    forum = Forum.objects.create(
        category=category, name="Django", description="Forum django"
    )
    return forum


def create_forum_public():
    category = create_category()
    forum = Forum.objects.create(
        category=category, name="Django_public",
        description="Forum django", public_forum=True
    )
    return forum


def create_topic(user):
    """
    Create topic example
    """
    forum = create_forum()
    topic = Topic.objects.create(
        forum=forum, user=user, title="test",
        date=timezone.now(), description="Test topic create",
        is_moderate=True, total_likes=0
    )
    return topic


def create_comment(user):
    """
    Create comment example
    """
    topic = create_topic(user)
    comment = Comment.objects.create(
        topic=topic, user=user, total_likes=0,
        date=timezone.now(), description="Test comment create"
    )
    return comment


def create_register(user):
    """
    Create register example
    """
    forum = create_forum()
    register = Register.objects.create(
        forum=forum, user=user
    )
    return register


def create_notification(user, topic):
    """
    Create notification example
    """
    notification = Notification.objects.create(
        user=user, is_seen=False, date=timezone.now(),
        content_object=topic
    )

    return notification


def create_topic_data_api(user, forum):
    """
    Data api for create topic via api rest
    """
    data = {
        "data": {
            "attributes": {
                "title": "Test title",
                "description": "<p>Example description</p>"
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
            "type": "topics"
        },
    }
    return data
