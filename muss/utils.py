import os
import shutil

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from muss.models import (
    Forum, Topic, Comment, Register, Profile
)


def basename(value):
    """
    This method return basename of one path.

    Args:
        value (str): Path.

    Returns:
        string: Basename path.
    """
    return os.path.basename(value)


def exists_folder(route):
    """
    This method verify that exists folder in base to route.

    Args:
        route (str): Path to check if exists.

    Returns:
        bool: Return if exists.
    """
    if os.path.exists(route):
        return True
    else:
        return False


def remove_folder(route_folder):
    """
    This method remove one folder.

    Args:
        route_folder (str): Path folder to remove.
    """
    try:
        shutil.rmtree(route_folder)
    except Exception:
        pass


def remove_file(route_file):
    """
    This method remove one file in base to route and image.

    Args:
        route_file (str): Path file to remove.
    """
    if route_file != "" and route_file is not None:
        if os.path.exists(route_file):
            os.remove(route_file)


def get_folder_attachment(topic):
    """
    This method return the path of one folder attachment for app forum.
    Args:
        topic (obj): Topic object.
    Returns:
        str: Path attachment.
    """
    folder = ""
    folder = "forum_" + str(topic.forum_id)
    folder = folder + "_user_" + str(topic.user.username)
    folder = folder + "_topic_" + str(topic.id_attachment)
    path_folder = os.path.join("forum", folder)
    media_path = settings.MEDIA_ROOT
    path = media_path + "/" + path_folder

    return path


def remove_folder_attachment(pk):
    """
    This method remove folder attachment and subtract one topic.

    Args:
        pk (int): Identification topic.
    """
    # Subtract one topic
    topic = get_object_or_404(Topic, pk=pk)
    forum = get_object_or_404(
        Forum, category__name=topic.forum.category.name,
        name=topic.forum, hidden=False
    )
    tot = forum.topics_count
    tot = tot - 1
    Forum.objects.filter(
        category__name=topic.forum.category.name,
        name=topic.forum, hidden=False
    ).update(
        topics_count=tot
    )

    path = get_folder_attachment(topic)

    # Remove attachment if exists
    if exists_folder(path):
        remove_folder(path)


def get_route_file(file_path, file_name):
    """
    This method build the path for a file MEDIA.

    Args:
        file_path (str): File path.
        file_name (str): File name.

    Returns:
        str: Concatenate file path + file name.
    """
    try:
        route_file = file_path + "/" + file_name
    except Exception:
        route_file = ""

    return route_file


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


def get_datetime_topic(date):
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


def get_photo_profile(user):
    """
    This method return photo profile.

    Args:
        user (int): Identification user.

    Returns:
        str: Path photo profile.
    """
    default_photo = static("muss/public/assets/images/profile.png")
    default_photo = settings.SITE_URL + default_photo
    profile = Profile.objects.filter(user=user)
    if profile.count() > 0:
        photo = profile[0].photo
        if photo:
            field_photo = settings.MEDIA_URL + str(photo)
        else:
            field_photo = default_photo
    else:
        field_photo = default_photo
    return field_photo


def is_user_moderator_forum(category, forum, user):
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


def user_can_create_topic(category, forum, user):
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
    is_register = Register.objects.filter(forum=forum, user=user).count()
    # If is superuser or moderator or is register in the forum
    if user.is_superuser or is_moderator or is_register > 0:
        return True
    else:
        return False


def get_total_forum_moderate_user(user):
    """
    Get total of forums that moderate one user.

    Args:
        user (obj): Object user.

    Returns:
        int: Total forum that user moderate.
    """
    return Forum.objects.filter(
        moderators=user
    ).count()


def check_moderate_topic_email(request, forum, obj):
    """
    Check if moderate topic and is moderate send email to moderators.

    Args:
        request (obj): Object request.
        forum (obj): Object forum.
        obj (obj): Object topic.

    Returns:
        obj: Object topic updated.
    """
    # If the forum is moderate
    if forum.is_moderate:
        # If is moderator, so the topic is moderate
        if request.user in forum.moderators.all():
            obj.is_moderate = True
        elif request.user.is_superuser:
            obj.is_moderate = True
        else:
            obj.is_moderate = False
    else:
        obj.moderate = True

    return obj


def check_topic_moderate(user, forum):
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


def get_domain(request):
    """
    Return main domain
    """
    protocol = 'https' if request.is_secure() else 'http'
    host = request.META['HTTP_HOST']
    return protocol + "://" + host


def get_url_topic(request, topic):
    """
    Get url topic
    """
    url = ""
    url += get_domain(request)
    url += "/topic/" + str(topic.pk) + "/" + topic.slug + "/"
    return url
