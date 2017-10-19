import json
from channels import Group


def data_base_realtime(obj, forum, is_topic):
    """
    Get data comment for new topic or new comment.

    Args:
        obj (obj): Object topic.
        forum (obj): Object forum.
        is_topic (bool): If is topic or comment.

    Returns:
        dict: Data base for realtime.
    """
    # Data necessary for realtime
    data = {
        "forum": forum.name,
    }

    if is_topic:
        data['topic'] = {
            'topicid': obj.pk,
            'slug': obj.slug,
            'title': obj.title,
            'username': obj.user.username,
            'userid': obj.user.pk,
            'isTop': obj.is_top,
        }
        data['comment'] = None
    else:
        data['comment'] = {
            'topicid': obj.topic.pk,
            'slug': obj.topic.slug,
            'title': obj.topic.title,
            'username': obj.user.username,
            'userid': obj.user.pk,
            'isTop': obj.topic.is_top,
        }
        data['topic'] = None

    return data


def new_topic_forum(forum, json_data_topic):
    """
    Send new topic to timeline forum

    Args:
        forum: Forum to send.
        json_data_topic (list): Data for create a new topic.
    """
    Group("forum-%s" % forum).send({
        'text': json.dumps(json_data_topic)
    })


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
