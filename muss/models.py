import os

from django.db.models import F
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.shortcuts import get_object_or_404
from django.template import defaultfilters
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from .validators import valid_extension_image


class Category(models.Model):
    """
    Model Category.

    - **parameters**:
        :param name: Name category.
        :description: Description category.
        :hidden: If a hidden category.
    """
    name = models.CharField(max_length=80)
    description = models.TextField(_('Description'), blank=True)
    hidden = models.BooleanField(
        blank=False, null=False, default=False,
        help_text=_('If checked, this category will be visible only for staff')
    )

    class Meta(object):
        ordering = ['name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Forum(models.Model):
    """
    Model Forum.

    - **parameters**:
        :param category: Category relation forum.
        :param parent: Parent forum.
        :param name: Name forum.
        :param description: Description forum.
        :param moderadors: Moderators of the forum.
        :param date: Date created forum.
        :param topic_count: Total topics that contains the forum.
        :param hidden: If a hidden forum.
        :param is_moderate: If the forum is moderated.
        :param public_forum: If the forum is public and don't to register
    """
    category = models.ForeignKey(
        Category, related_name='categories',
        verbose_name=_('Category'), on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self', related_name='parents', verbose_name=_('Parent forum'),
        blank=True, null=True, on_delete=models.CASCADE
    )
    name = models.CharField(_('Name'), max_length=80)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(max_length=100, editable=False)
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='moderators',
        verbose_name=_('Moderators')
    )
    date = models.DateTimeField(
        _('Date'), blank=True, null=True, auto_now_add=True, editable=False
    )
    topics_count = models.IntegerField(
        _('Total topics'), blank=True, default=0, editable=False,
    )
    hidden = models.BooleanField(
        _('Hidden'), blank=False, null=False, default=False,
        help_text=_('If hide the forum in the index page')
    )
    is_moderate = models.BooleanField(
        _('Check topics'), default=False,
        help_text=_('If the forum is moderated')
    )
    public_forum = models.BooleanField(
        _('Public'), default=False,
        help_text=_(
            "If the forum is public and don't to register to the forum"
        )
    )

    class Meta(object):
        unique_together = ('category', 'name', )
        ordering = ['category', 'name']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __str__(self):
        return self.name

    # Return forums that moderating one moderator
    def tot_forums_moderators(self, moderator):
        tot = self.__class__.objects.filter(
            moderators=moderator
        ).count()

        return tot

    # Add permissions topic to moderator
    def add_permissions_topic_moderator(self, moderator):
        permission1 = Permission.objects.get(codename='add_topic')
        permission2 = Permission.objects.get(codename='change_topic')
        permission3 = Permission.objects.get(codename='delete_topic')

        moderator.user_permissions.add(permission1, permission2, permission3)

        # Add permission is_staff
        moderator.is_staff = True
        moderator.save()

    # Clear permissions to moderator
    def clear_permissions_moderator(self, moderator):
        moderator.user_permissions.clear()

        # Remove permission is_staff
        moderator.is_staff = False
        moderator.save()

    # Remove permission in user moderators
    def remove_user_permissions_moderator(self):
        for moderator in self.moderators.all():
            # Superuser not is necessary
            if not moderator.is_superuser:
                # Return forums that moderating one moderator
                tot_forum_moderator = self.tot_forums_moderators(moderator)

                # Only remove permissions if is moderator one forum
                if tot_forum_moderator < 1:
                    self.clear_permissions_moderator(moderator)

    def delete(self, *args, **kwargs):
        for moderator in self.moderators.all():
            if not moderator.is_superuser:
                # Only remove permissions if is moderator has one forum
                if self.tot_forums_moderators(moderator) < 1:
                    # Remove permissions to user
                    self.clear_permissions_moderator(moderator)

        super(Forum, self).delete()

    def save(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.name)
        super(Forum, self).save(*args, **kwargs)

    def clean(self):
        if self.name:
            self.name = self.name.strip()

    def forum_description(obj):
        return obj.description
    forum_description.allow_tags = True
    forum_description.short_description = _("Description")


class MessageForum(models.Model):
    """
    Message forum model.

    - **parameters**:
        :param forum: Forum relation.
        :param message_information: Message to inform the forum.
        :param message_expire_from: Date expire 'from'.
        :param message_expire_to: Date expire 'to'.
    """
    forum = models.ForeignKey(
        Forum, related_name='message_information', verbose_name=_('Forum'),
        on_delete=models.CASCADE
    )
    message_information = models.TextField(
        _('Message to inform'), blank=False, null=False,
        help_text=_('If you want to report a message to a forum')
    )
    message_expires_from = models.DateTimeField(
        _('Message expires from'), blank=False, null=False,
        help_text=_('Date from message expired')
    )
    message_expires_to = models.DateTimeField(
        _('Message expires to'), blank=False, null=False,
        help_text=_('Date to message expired')
    )

    class Meta(object):
        verbose_name = _('Message for forums')
        verbose_name_plural = _('Messages for forums')

    def __str__(self):
        return self.message_information


class Topic(models.Model):
    """
    Model Topic.

    - **parameters**:
        :param forum: Forum that contains the topic.
        :param user: User that created the topic.
        :param slug: Slug url.
        :param title: Title topic.
        :param date: Date created the topic.
        :param last_activity: Last activity topic.
        :param description: Content of the topic.
        :param id_attachment: Identification attchment file.
        :param attachment: Path attchment file.
        :param is_close: If the topic is closed.
        :param is_moderate: If the topic is moderated.
        :param is_top: If the topic go to top in the forum.
        :param: total_likes: Total likes of the topic.
    """
    def generate_path(instance, filename):
        """
        Generate path to field Attchment
        """
        folder = ""
        folder = "forum_" + str(instance.forum_id)
        folder = folder + "_user_" + str(instance.user)
        folder = folder + "_topic_" + str(instance.id_attachment)
        return os.path.join("forum", folder, filename)

    forum = models.ForeignKey(
        Forum, related_name='forums', verbose_name=_('Forum'),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='users', verbose_name=_('User'),
        on_delete=models.CASCADE
    )
    slug = models.SlugField(max_length=100)
    title = models.CharField(_('Title'), max_length=80)
    date = models.DateTimeField(
        _('Date'), blank=False, auto_now=True, db_index=False
    )
    last_activity = models.DateTimeField(
        _('Last activity'), blank=False, auto_now=True, db_index=False
    )
    description = models.TextField(_('Description'), blank=False, null=False)
    id_attachment = models.CharField(max_length=200, null=True, blank=True)
    attachment = models.FileField(
        _('File'), blank=True, null=True, upload_to=generate_path,
        validators=[valid_extension_image]
    )
    is_close = models.BooleanField(
        _('Closed topic'), default=False,
        help_text=_('If the topic is closed')
    )
    is_moderate = models.BooleanField(
        _('Moderate'), default=False,
        help_text=_('If the topic is moderated')
    )
    is_top = models.BooleanField(
        _('Top'), default=False,
        help_text=_('If the topic is important and it will go top')
    )
    total_likes = models.PositiveIntegerField(default=0, editable=False)

    class Meta(object):
        ordering = ['-is_top', 'forum', '-date', 'title', '-last_activity']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        pk = self.pk
        forum = self.forum_id

        topic = get_object_or_404(Topic, pk=pk)

        folder = ""
        folder = "forum_" + str(forum)
        folder = folder + "_user_" + str(topic.user.username)
        folder = folder + "_topic_" + str(topic.id_attachment)
        path_folder = os.path.join("forum", folder)
        media_path = settings.MEDIA_ROOT
        path = media_path + "/" + path_folder

        # Remove attachment if exists
        from .utils import remove_folder, exists_folder
        if exists_folder(path):
            remove_folder(path)

        Topic.objects.filter(pk=pk).delete()
        self.update_forum_topics(
            self.forum.category.name, self.forum, "subtraction"
        )

    def save(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.title)
        if not self.pk:
            self.update_forum_topics(
                self.forum.category.name, self.forum, "sum"
            )

        self.generate_id_attachment(self.id_attachment)
        super(Topic, self).save(*args, **kwargs)

    def update_forum_topics(self, category, forum, action):
        """
        Update topic count
        """
        f = Forum.objects.get(category__name=category, name=forum)
        tot_topics = f.topics_count
        if action == "sum":
            Forum.objects.filter(name=forum).update(
                topics_count=F('topics_count') + 1
            )
        elif action == "subtraction":
            Forum.objects.filter(name=forum).update(
                topics_count=F('topics_count') - 1
            )

    def generate_id_attachment(self, value):
        """
        Generate id for attchments files
        """
        if not value:
            self.id_attachment = get_random_string(length=32)


class Comment(models.Model):
    """
    Model Comment.

    - **parameters**:
        :param topic: Topic to which the commentary belongs.
        :param user: User that created the comment.
        :param date: Date that created the comment.
        :param description: Content comment.
        :param total_likes: Total likes of the comment.
    """
    topic = models.ForeignKey(
        Topic, related_name='topics', verbose_name=_('Topic'),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comment_users',
        verbose_name=_('User'), on_delete=models.CASCADE
    )
    date = models.DateTimeField(
        _('Date'), blank=True, auto_now=True, db_index=True
    )
    description = models.TextField(_('Description'), blank=True)
    total_likes = models.PositiveIntegerField(default=0, editable=False)

    class Meta(object):
        ordering = ['date']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return str(self.description)


class Notification(models.Model):
    """
    Model Notification.

    - **parameters**:
        :param content_object: Relation topic or comment.
        :param user: Identification user that belong the notification.
        :param is_seen: If the notification is seen
        :param date: Date notification.
    """
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
    )
    id_object = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'id_object')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notifications_user',
        null=False, blank=False,
    )
    is_seen = models.BooleanField(default=0)
    date = models.DateTimeField(blank=True, db_index=True)

    class Meta(object):
        ordering = ['date']

    def __str__(self):
        return str(self.id_object)


class LikeTopic(models.Model):
    """
    Model LikeTopic.

    - **parameters**:
        :param topic: Topic that gave it 'like'.
        :param users: Data with tee users that created the 'like'.
    """
    topic = models.OneToOneField(
        Topic, related_name='likes_topic', on_delete=models.CASCADE
    )
    users = JSONField()

    def __str__(self):
        return str(self.topic.pk)


class LikeComment(models.Model):
    """
    Model LikeComment.

    - **parameters**:
        :param comment: Coment that gave it 'like'.
        :param users: Data with the users that created the 'like'.
    """
    comment = models.OneToOneField(
        Comment, related_name='likes_comment', on_delete=models.CASCADE
    )
    users = JSONField()

    def __str__(self):
        return str(self.comment.pk)


class Register(models.Model):
    """
    Model Register.

    - **parameters**:
        :param forum: Forum to which it was registered.
        :param user: User that registered.
        :param date: Date that registered.
    """
    forum = models.ForeignKey(
        Forum, related_name='register_forums', verbose_name=_('Forum'),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='register_users',
        verbose_name=_('User'), on_delete=models.CASCADE
    )
    date = models.DateTimeField(
        _('Date'), blank=True, auto_now=True, db_index=True
    )

    class Meta(object):
        ordering = ['date']
        verbose_name = _('Register')
        verbose_name_plural = _('Registers')

    def __str__(self):
        return str(self.forum) + " " + str(self.user)


class Profile(models.Model):
    """
    Model Profile.

    - **parameters**:
        :param user: User that belong to profile.
        :param photo: Photo profile.
        :param about: Content 'about' the of profile.
        :param activation_key: Activation key authentication.
        :param key_expire: Key activate expire authentication.
        :param is_troll: If the user is troll.
        :param receive_emails: Check if receive emails.
    """
    def generate_path_profile(instance, filename):
        """
        Generate path to field photo
        """
        return os.path.join(
            "profiles", "profile_" + str(instance.user_id), filename
        )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="user", db_index=True,
        on_delete=models.CASCADE
    )
    photo = models.FileField(
        _("Photo"), upload_to=generate_path_profile, null=True, blank=True,
    )
    about = models.TextField(_("About me"), blank=True, null=True)
    location = models.CharField(
        _("Location"), max_length=200, null=True, blank=True
    )
    activation_key = models.CharField(max_length=100, null=False, blank=False)
    key_expires = models.DateTimeField(auto_now=False)
    is_troll = models.BooleanField(
        _('Is troll'), default=False,
        help_text=_('If the user is troll')
    )
    receive_emails = models.BooleanField(
        _('Receive Emails'), default=True,
        help_text=_('If receive Emails')
    )

    def __str__(self):
        return str(self.user.username)

    def last_seen(self):
        """
        Get last seen
        """
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        """
        Check if is online profile
        """
        if self.last_seen():
            now = timezone.now()
            if now > self.last_seen() + timezone.timedelta(
                         seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False


class Configuration(models.Model):
    """
    Model configuration muss like logo and class css.

    - **parameters**:
        :param site: Site relation.
        :param logo: Logo forum.
        :param favicon: Favicon forum.
        :param logo_width: Width logo forum.
        :param logo_height: Height logo forum.
        :param custom_css: Personalization css of the forum.
        :description: Description site.
        :keyword: Keywords for the SEO.
    """
    def generate_path_configuration(instance, filename):
        """
        Generate path to field logo
        """
        return os.path.join(
            "configuration", filename
        )

    site = models.OneToOneField(Site)
    logo = models.FileField(
        upload_to=generate_path_configuration, null=True, blank=True,
    )
    favicon = models.FileField(
        upload_to=generate_path_configuration, null=True, blank=True,
    )
    logo_width = models.PositiveIntegerField(
        _("Logo width"), null=True, blank=True,
        help_text=_('In pixels')
    )
    logo_height = models.PositiveIntegerField(
        _("Logo height"), null=True, blank=True,
        help_text=_('In pixels')
    )
    custom_css = models.TextField(
        _("Custom design"), null=True, blank=True
    )
    description = models.TextField(
        _('Description'), blank=True,
        help_text=_("Description site.")
    )
    keywords = models.TextField(
        _('Keywords'), blank=True,
        help_text=_("Keywords for the SEO.")
    )

    class Meta(object):
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')

    def __str__(self):
        return str(self.site)


class HitcountTopic(models.Model):
    """
    Model for hit count topic.

    - **parameters**:
        :param topic: Topic relation.
        :param data: Data sessions
    """
    topic = models.ForeignKey(Topic, related_name='topichitcount')
    data = JSONField()
