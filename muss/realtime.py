import json
from channels import Group
from django.conf import settings


def data_base_realtime(obj, photo, forum, is_topic):
    """
    Get data comment for new topic or new comment.

    Args:
        obj (obj): Object topic.
        photo: Photo topic.
        forum (obj): Object forum.
        is_topic (bool): If is topic or comment.

    Returns:
        dict: Data base for realtime.
    """
    # Data necessary for realtime
    data = {
        "settings_static": settings.STATIC_URL,
        "forum": forum,
        "category": obj.forum.category.name,
        "photo": photo,
    }

    record = {
        'topicid': obj.pk,
        'slug': obj.slug,
        'title': obj.title,
        'username': obj.user.username,
        'userid': obj.user.pk
    }

    if is_topic:
        data['topic'] = record
        data['comment'] = None
    else:
        data['comment'] = record
        data['topic'] = None

    return data


def new_notification(data_notification, list_us):
    """
    Send new notification topic or comment to redis.

    Args:
        data_notification (list): Data for create a new notification.
        list_us (list(str)): List users to send new notification.
    """
    # Add to real time new notification
    json_data_notification = json.dumps(data_notification)

    for user in list_us:
        Group("notification-%s" % user.id).send({
            'text': json_data_notification
        })


def new_comment(data_comment, comment_description):
    """
    Send new comment.

    Args:
        data_comment (list): Data for create a new comment.
        comment_description (str): Comment description.
    """
    topic = data_comment['comment']['topicid']
    # Publish new comment in topic
    data_comment['description'] = comment_description
    json_data_comment = json.dumps(data_comment)
    Group("topiccomment-%s" % topic).send({
        'text': json_data_comment
    })
