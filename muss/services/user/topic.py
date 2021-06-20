from muss.models import Comment, Forum, Register
from muss.services.user.forum import is_user_moderator_forum


def get_users_topic(topic, myuser):
    """
    This method return all users of one topic, else my user.

    Args:
        topic (object): Topic object.
        myuser (int): Identification user logged.

    Returns:
        list(int): List users that commented in the topic.
        list(int): List emails that commented in the topic.
    """
    comments = Comment.objects.filter(topic_id=topic.pk)
    list_us = []
    list_emails = []
    for comment in comments:
        if comment.user_id != myuser:
            if not (comment.user in list_us):
                list_us.append(comment.user)
                if comment.user.user.receive_emails:
                    list_emails.append(comment.user.email)

    return list_us, list_emails


def user_can_create_topic(category: str, forum: Forum, user) -> bool:
    """
    Check if user can create topic.

    Args:
        category (str): Category name.
        forum (obj): Object forum.
        user (obj): Object user.

    Returns:
        bool: If the user can create topic.
    """
    is_moderator = is_user_moderator_forum(category, forum, user)
    register_count = Register.objects.filter(forum=forum, user=user).count()

    if forum.public_forum:
        is_register = True
    else:
        if register_count > 0:
            is_register = True
        else:
            is_register = False

    # If is superuser or moderator or is register in the forum
    if user.is_superuser or is_moderator or is_register:
        return True
    else:
        return False
