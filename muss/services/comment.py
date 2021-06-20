from muss import (
    notifications_email as nt_email,
    realtime, notifications as nt
)
from muss.models import Comment, Topic


def create_comment(user, serializer: Comment, topic: Topic, url: str):
    """
    Create a new comment
    """

    # Save the record comment
    comment = serializer.save(
        topic=topic, user=user
    )

    # Send notifications comment
    params = nt.get_users_and_send_notification_comment(user, topic, comment)
    list_us = params['list_us']
    list_email = params['list_email']

    # Send email
    nt_email.send_mail_comment(str(url), list_email)

    # Data necessary for realtime
    data = realtime.data_base_realtime(
        comment, topic.forum, False
    )

    # Send new notification realtime
    realtime.new_notification(data, list_us)

    # Send new comment in realtime
    realtime.new_comment(data, comment.description)
