from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from muss.utils import get_users_topic
from muss.models import Notification


def get_notifications(user):
    """
    This method return Notification of one user.

    Args:
        user (int): Identification user.

    Returns:
        list(Notification): Notification of user.
    """
    try:
        notif = Notification.objects.filter(user=user).order_by("-date")
    except Notification.DoesNotExist:
        notif = None

    return notif


def save_notification_model(related_object, id_object, user):
    """
    Save new notificaiton.

    Args:
        related_object (obj): Object related (Topic or Comment).
        id_object (int): Id object.
        user (int): Identification user.
    """
    now = timezone.now()
    notification = Notification(
        user=user, is_seen=False,
        id_object=id_object, date=now,
        content_type=related_object
    )
    notification.save()


def get_moderators_and_send_notification_topic(request, forum, topic):
    """
    Get list moderators to send notification for realtime
    and send notificaiton to model Notification for topic.

    Args:
        request (obj): Object request.
        forum (obj): Object forum.
        topic (obj): Object topic.

    Returns:
        list(int): List users.
    """
    # Get moderators forum
    list_us = []

    related_object = ContentType.objects.get_for_model(topic)
    for moderator in forum.moderators.all():
        # If not is my user
        if moderator.id != request.user.id:
            # Send notification to moderator
            save_notification_model(
                related_object, topic.pk, moderator
            )
            list_us.append(moderator.id)

    return list_us


def get_users_and_send_notification_comment(request, topic, comment):
    """
    Get list users to send notification for realtime
    and send notificaiton to model Notification for comment.

    Args:
        request (obj): Object request.
        forum (obj): Object forum.
        comment (obj): Object comment.

    Returns:
        dict: List users and list_emails.
    """
    now = timezone.now()

    myuser = request.user
    # Send notifications
    list_us, list_emails = get_users_topic(topic, myuser.id)

    # If not exists user that create topic, add
    user_original_topic = topic.user
    user_email = topic.user.email
    comment_user = comment.user

    # If the notificacion is mine send to all but not to me
    if user_original_topic == myuser and comment_user == myuser:
        # Not make nothing but list_user is already
        # Not send email
        pass
    # If the notificacion is mine send to all but not to create to comment
    elif user_original_topic == myuser and comment_user != myuser:
        # The user comment not exists in list_us
        # Add user that created topic
        list_us.append(user_original_topic)
        # Add user for send email
        list_emails.append(user_email)
    # If the notificacion not is mine send to all but not to me
    elif user_original_topic != myuser and comment_user == myuser:
        # Check if exists the created topic
        if not(user_original_topic in list_us):
            # Send to created topic
            list_us.append(user_original_topic)

        # Add user for send email to created topic
        list_emails.append(user_email)
    # If the notificacion not is mine send to all but not to create to comment
    elif user_original_topic != myuser and comment_user != myuser:
        # Check if exists the created topic
        if not(user_original_topic in list_us):
            # Send to created topic
            list_us.append(user_original_topic)

        # Add user for send email to created topic
        list_emails.append(user_email)

    # Get content type for comment model
    related_object_type = ContentType.objects.get_for_model(comment)
    for user in list_us:
        save_notification_model(
            related_object_type, comment.pk, user
        )

    return {
        'list_us': list_us,
        'list_email': list_emails
    }
