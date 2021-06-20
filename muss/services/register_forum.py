from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from muss import notifications_email as nt_email
from muss.models import Forum, Register


def get_all_registers(user: str, forum: str,
                      queryset: QuerySet) -> QuerySet:
    """
    Get register members (all)
    """

    user_id = int(user)
    forum_id = int(forum)

    return queryset.filter(
        forum__pk=forum_id, user__pk=user_id
    )


def get_register_by_members(forum_id: str):
    """
    Get register by filter members only (without moderators)
    """

    forum_id = int(forum_id)
    # Get register users
    forum = get_object_or_404(
        Forum, pk=forum_id, hidden=False
    )
    moderators = forum.moderators.all()
    # Get registers, exclude moderators
    return forum.register_forums.filter(
        ~Q(user__in=moderators), is_enabled=True
    )


def create_register(forum: Forum, user) -> int:
    """
    Create a new register
    """

    exists_register = Register.objects.filter(
        forum_id=forum.pk, user=user
    )

    total = exists_register.count()

    # If the register not exists
    if total == 0:
        nt_email.send_email_new_register_to_moderators(forum, user)

    return total
