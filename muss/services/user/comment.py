from muss.models import Topic
from muss.services.user.profile import get_photo_profile


def get_users_who_commented_topic(username_topic: str, obj: Topic) -> list:
    """
    GUsers who commented on a topic
    """

    users = []
    list_users = []

    for comment in obj.topics.all():
        comment_user = comment.user
        username = comment_user.username
        if not (username in list_users):
            photo = get_photo_profile(comment_user.id)
            record = {
                "username": username,
                "photo": photo
            }
            # If is creator topic, add top
            if username == username_topic:
                users.insert(0, record)
            else:
                users.append(record)
            list_users.append(username)

    # If creator topic not exists, add
    if not (username_topic in list_users) and obj.topics.count() > 0:
        photo = get_photo_profile(obj.user.id)
        users.insert(0, {
            "username": username_topic,
            "photo": photo
        })

    return users
