import base64
import hashlib
import random

from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from muss.email import send_mail


def send_welcome_email(email, username, activation_key):
    """
    This method send email for confirm user.

    Args:
        email (str): Email user.
        username (str): Username.
        activation_key (str): Activation Key user.
    """
    username = base64.b64encode(username.encode("utf-8")).decode("ascii")
    content = _(
        "Thank you for joining to %(site)s "
        "please enter to confirm your email to this address:"
    ) % {
        'site': settings.SITE_NAME
    }

    url = reverse('confirm_email')
    urlContent = url + username + "/" + activation_key + "/"
    current_site = Site.objects.get_current()
    send_mail(
        _("Welcome to " + settings.SITE_NAME),
        _(content) + current_site.domain + urlContent,
        settings.EMAIL_MUSS,
        [email],
        fail_silently=False
    )


def get_data_confirm_email(email):
    """
    This method return info for email confirm.

    Args:
        email (str): Email user.

    Returns:
        dict: Activation key and key expires user.
    """
    salt = hashlib.sha1(str(random.random()).encode("utf-8")).hexdigest()[:5]
    key = salt.encode("utf-8") + email.encode("utf-8")
    activation_key = hashlib.sha1(key).hexdigest()
    key_expires = timezone.now() + timezone.timedelta(2)

    return {
        'activation_key': activation_key,
        'key_expires': key_expires
    }


def send_mail_new_register(email_moderator, forum, user):
    """
    Send email new register.

    Args:
        email_moderator (str): Email moderator.
        forum (obj): Forum object.
        user (obj): User object.
    """
    title_email = _("New register in %(forum)s ") % {'forum': forum.name}
    message = _("New registered user %(user)s to the forum: %(forum)s") % {
        'forum': forum.name,
        'user': user.username,
    }
    email_from = settings.EMAIL_MUSS

    if email_from:
        send_mail(
            title_email, message, email_from,
            [email_moderator], fail_silently=False
        )


def send_mail_comment(url, list_email):
    """
    Send email comment.

    Args:
        url (str): Url site.
        list_email (list(str): List email to send mail.
    """
    title_email = _("New comment in %(site)s") % {
        'site': settings.SITE_NAME
    }

    message = _("You have one new comment in the topic: %(site)s") % {
        'site': url
    }

    email_from = settings.EMAIL_MUSS
    if email_from:
        send_mail(
            title_email, message, email_from,
            list_email, fail_silently=False
        )


def send_mail_topic(email_moderator, forum, topic, domain):
    """
    Send email topic.

    Args:
        email_moderator (str): Email moderator.
        forum (obj): Forum object.
        topic (obj): Topic object.
        domain (str): Domain url.
    """
    # Send email to moderator
    site = domain + "/forum/" + str(forum.pk) + "/" + forum.slug

    # Url topic
    url_topic = ""
    url_topic += domain
    url_topic += "/topic/" + str(topic.pk) + "/" + topic.slug + "/"

    site_name = settings.SITE_NAME
    title_email = _("New topic in %(site)s ") % {'site': site_name}
    message = _("Added a new topic %(url_topic)s to the forum: %(site)s") % {
        'site': site,
        'url_topic': url_topic,
    }
    email_from = settings.EMAIL_MUSS

    if email_from:
        send_mail(
            title_email, message, email_from,
            [email_moderator], fail_silently=False
        )


def send_mail_reset_password(
        subject_template_name, email_template_name,
        context, from_email, to_email):
    """
    Send email reset password
    """
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    if to_email:
        send_mail(
            subject, body, from_email, [to_email]
        )


def send_notification_topic_to_moderators(forum, topic, domain):
    """
    Send email topic to moderators.

    Args:
        forum (obj): Forum object.
        topic (obj): Topic object.
        domain (str): Domain url.
    """
    # If the user who created the topic is not a moderator
    if not (topic.user in forum.moderators.all()):
        # Get moderators forum
        for moderator in forum.moderators.all():
            if moderator.user.receive_emails:
                # Send email
                send_mail_topic(moderator.email, forum, topic, domain)


def send_email_new_register_to_moderators(forum, user):
    """
    Send email new register to moderators.

    Args:
        forum (obj): Forum object.
        user (user): User object.
    """
    # If the user who created the topic is not a moderator
    if not (user in forum.moderators.all()):
        # Get moderators forum
        for moderator in forum.moderators.all():
            # Send email
            send_mail_new_register(moderator.email, forum, user)
