from django.db.models import Q, QuerySet
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils import timezone

from muss import notifications_email as nt_email, notifications as nt, realtime
from muss.models import Forum, Topic


def check_moderate_topic_email(user, forum: Forum, obj: Topic) -> Topic:
    """
    Check if moderate topic and is moderate send email to moderators.

    Args:
        user (obj): Object user logged.
        forum (obj): Object forum.
        obj (obj): Object topic.

    Returns:
        obj: Object topic updated.
    """

    # If the forum is moderate
    if forum.is_moderate:
        # If is moderator, so the topic is moderate
        if user in forum.moderators.all():
            obj.is_moderate = True
        elif user.is_superuser:
            obj.is_moderate = True
        else:
            obj.is_moderate = False
    else:
        obj.moderate = True

    return obj


def check_topic_moderate(user, forum: Forum) -> bool:
    """
    Check if one topic is mark like moderate
    """

    # If is superuser
    if user.is_superuser:
        return True
    # If the forum not is moderate
    elif not forum.is_moderate:
        return True
    # If user is moderator
    elif user in forum.moderators.all():
        return True
    else:
        return False


def filter_topic_by_filter(params: QueryDict, queryset: QuerySet) -> QuerySet:
    """
    Filter topics by type of filter
    """

    type_filter = params.get('filter')
    pk = params.get('pk')
    slug = params.get('slug')
    search_title = params.get('title')
    suggest = params.get('suggest')
    username = params.get('username')

    data = queryset
    if type_filter == 'only_topic' and pk and slug:
        # Get only topic
        data = queryset.filter(
            pk=pk, slug=slug, is_moderate=True
        )
    elif type_filter == 'by_forum' and slug:
        # Filter topics by forum
        data = queryset.filter(
            forum__slug=slug, is_moderate=True
        )
    elif type_filter == 'search' and search_title:
        # Search topics
        data = queryset.annotate(
            search=SearchVector('title', 'description')
        ).filter(search=SearchQuery(search_title), is_moderate=True)

    elif type_filter == "by_user" and username:
        # Filter by user topic
        data = queryset.filter(
            user__username=username, is_moderate=True
        )
    elif type_filter == "latest":
        # Get the latest 10 topics
        data = queryset.filter(
            is_moderate=True).order_by("-date")[:10]
    elif type_filter == 'suggests' and suggest:
        # Filter suggest topic
        topic = get_object_or_404(
            Topic, pk=suggest, is_moderate=True
        )
        words = topic.title.split(" ")
        condition = Q()
        for word in words:
            condition |= Q(title__icontains=word)

        data = Topic.objects.filter(
            condition, Q(forum__pk=topic.forum_id, is_moderate=True)
        ).exclude(
            pk=topic.pk
        )[:10]

    return data


def create_topic(user, forum: Forum, serializer: Topic, domain: str) -> None:
    """
    Create a new topic
    """

    # Check if moderation topic
    is_moderate = check_topic_moderate(
        user, forum
    )
    # If the forum is moderate send email
    serializer = check_moderate_topic_email(
        user, forum, serializer
    )

    # Save record
    topic = serializer.save(
        forum=forum, user=user, is_moderate=is_moderate
    )

    # If is moderate send notifications
    if is_moderate:
        # Send email to moderators
        nt_email.send_notification_topic_to_moderators(
            forum, topic, domain
        )

        # Get moderators forum and send notification
        list_us = nt.get_moderators_and_send_notification_topic(
            user, forum, topic
        )

        # Data necessary for realtime
        data = realtime.data_base_realtime(
            topic, forum, True
        )

        # Send new notification realtime
        realtime.new_notification(data, list_us)

        # Send new topic in forum
        realtime.new_topic_forum(forum.pk, data)


def get_datetime_topic(date) -> int:
    """
    This method return info one datetime for topic or notification.

    Args:
        date (datetime): Datetime topic.

    Returns:
        ste: Time elapsed.
    """
    flag = True
    now = timezone.now()
    # If is beteween 1 and 10 return days
    difference = (now - date).days

    # If is this days return hours
    if difference == 0:
        flag = False
        diff = now - date
        minutes = (diff.seconds // 60) % 60
        hours = diff.seconds // 3600
        if minutes < 60 and hours == 0:
            difference = "%s %s" % (
                _("ago"), str((diff.seconds // 60) % 60) + "m ")
        else:
            difference = "%s %s" % (_("ago"), str(diff.seconds // 3600) + "h ")

    # If is days
    if flag:
        difference = "%s %s %s" % (_("ago"), str(difference), _("days ago"))

    return difference
