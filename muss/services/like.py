from django.db.models import F
from muss.models import Comment, LikeComment, LikeTopic, Topic


def create_like_topic(user: int, topic_pk: int) -> None:
    """
    Create like topic
    """

    lt = LikeTopic.objects.filter(topic__pk=topic_pk)
    if lt.exists():
        s = lt.filter(users__contains=[{'user': user}])
        if not s.exists():
            # Not exists, then i add the user
            record = lt.first()
            users = record.users
            # Insert new user to existing users
            users.append({'user': user})
            record.users = users
            # Update record in the field users
            record.save()

            # Increment total like
            Topic.objects.filter(pk=topic_pk).update(
                total_likes=F('total_likes') + 1
            )
    else:
        topic = Topic.objects.filter(pk=topic_pk)
        LikeTopic.objects.create(
            topic=topic.first(), users=[{'user': user}]
        )

        # Increment total like
        topic.update(
            total_likes=F('total_likes') + 1
        )


def delete_like_topic(pk: int, user_pk: int) -> None:
    """
    Delete like topic
    """

    lt = LikeTopic.objects.filter(topic__pk=pk).first()
    users = lt.users

    for i, d in enumerate(users):
        if d['user'] == user_pk:
            users.pop(i)
            break

    lt.users = users
    lt.save()

    # Decrement like in total like
    Topic.objects.filter(pk=pk).update(
        total_likes=F('total_likes') - 1
    )


def create_like_comment(user: int, comment_pk: int) -> None:
    """
    Create like comment
    """

    lc = LikeComment.objects.filter(comment__pk=comment_pk)
    if lc.exists():
        s = lc.filter(users__contains=[{'user': user}])
        if not s.exists():
            # Not exists, then i add the user
            record = lc.first()
            users = record.users
            # Insert new user to existing users
            users.append({'user': user})
            record.users = users
            # Update record in the field users
            record.save()

            # Increment total like
            Comment.objects.filter(pk=comment_pk).update(
                total_likes=F('total_likes') + 1
            )
    else:
        comment = Comment.objects.filter(pk=comment_pk)
        LikeComment.objects.create(
            comment=comment.first(), users=[{'user': user}]
        )

        # Increment total like
        comment.update(
            total_likes=F('total_likes') + 1
        )


def delete_like_comment(pk: int, user_pk: int) -> None:
    """
    Delete like comment
    """

    lc = LikeComment.objects.filter(comment__pk=pk).first()
    users = lc.users

    for i, d in enumerate(users):
        if d['user'] == user_pk:
            users.pop(i)
            break

    lc.users = users
    lc.save()

    # Decrement like in total like
    Comment.objects.filter(pk=pk).update(
        total_likes=F('total_likes') - 1
    )
