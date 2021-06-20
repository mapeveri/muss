from django.shortcuts import get_object_or_404
from muss.models import Forum, Profile, Register


def check_permissions_forum_user(user_id: int, forum_id: int) -> dict:
    """
    Check permission forum by user
    """

    response = {
        'register': False,
        'is_moderator': False,
        'is_troll': False,
        'is_pending_moderate': False,
    }

    # Check if user is registered in the forum
    register = Register.objects.filter(
        user__pk=user_id, forum__pk=forum_id
    )

    if register.count() > 0:
        if register.first().is_enabled:
            response['register'] = True
        else:
            response['is_pending_moderate'] = True

    # Check if user logged is moderator in the forum
    total_moderator = Forum.objects.filter(
        pk=forum_id, moderators__in=[user_id]
    ).count()

    if total_moderator > 0:
        response['is_moderator'] = True

    # Check if user logged is a troll
    profile = Profile.objects.filter(user__id=user_id)
    if profile.exists():
        response['is_troll'] = profile.first().is_troll

    return response


def get_forums_by_user(username: str) -> list:
    """
    Get forums by user
    """

    list_forums = []
    registers = Register.objects.filter(
        user__username=username
    )
    for register in registers:
        forum = register.forum
        list_forums.append({
            'name': forum.name,
            'slug': forum.slug,
            'id': register.forum_id,
            'moderator': False
        })
    forums = Forum.objects.filter(
        moderators__username__in=[username]
    )
    for forum in forums:
        list_forums.append({
            'name': forum.name,
            'slug': forum.slug,
            'id': forum.pk,
            'moderator': True
        })

    return list_forums


def is_user_moderator_forum(category: str, forum: Forum, user) -> bool:
    """
    Check if user is moderator forum.

    Args:
        category (str): Category name.
        forum (obj): Object forum.
        user (obj): Object user.

    Returns:
        bool: If the user is moderator forum.
    """
    forum = get_object_or_404(Forum, category__name=category, name=forum)
    if user in forum.moderators.all():
        return True
    else:
        return False
