from django.db import router
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import helpers
from django.contrib.admin.utils import get_deleted_objects
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from admin_interface.models import Theme

from muss import (
    forms, models, utils, notifications_email as nt_email,
    realtime, notifications as nt
)
from muss.services.topic import check_topic_moderate


class TopicAdmin(admin.ModelAdmin):
    form = forms.FormAdminTopic
    list_display = ('title', 'forum', 'date', 'is_moderate', 'is_close')
    list_filter = ['title', 'date', 'is_moderate', 'is_close']
    search_fields = ['title', 'date', 'is_moderate', 'is_close']
    actions = ['delete_topic']

    def get_queryset(self, request):
        qs = super(TopicAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        forums = models.Forum.objects.filter(
            moderators=request.user.id
        )
        lista = []
        for f in forums:
            lista.append(f.pk)

        return qs.filter(forum_id__in=lista)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "forum":
                kwargs["queryset"] = models.Forum.objects.filter(
                    moderators=request.user.id
                )
            if db_field.name == "user":
                User = get_user_model()
                kwargs["queryset"] = User.objects.filter(
                    pk=request.user.id
                )
        return super(TopicAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_actions(self, request):
        actions = super(TopicAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        is_moderate = False
        forum = obj.forum
        forum_id = obj.forum_id

        if not change:
            is_moderate = check_topic_moderate(
                request.user, forum
            )
            instance.is_moderate = is_moderate

        instance.save()

        # Check if is create and is_moderate topic
        if not change and is_moderate:
            domain = utils.get_domain(request)
            # Send email to moderators
            nt_email.send_notification_topic_to_moderators(
                forum, obj, domain
            )

            # Get moderators forum and send notification
            list_us = nt.get_moderators_and_send_notification_topic(
                request.user, forum, obj
            )

            # Data necessary for realtime
            data = realtime.data_base_realtime(
                obj, forum, True
            )

            # Send new notification realtime
            realtime.new_notification(data, list_us)

            # Send new topic in forum
            realtime.new_topic_forum(forum_id, data)

    def delete_topic(self, request, queryset):
        """
        This method remove topic's selected in the admin django.
        Can remove one o more records.
        """
        if not self.has_delete_permission(request):
            raise PermissionDenied

        if request.POST.get("post"):
            for obj in queryset:
                topic_id = obj.pk
                # Delete record
                models.Topic.objects.filter(pk=topic_id).delete()

            n = queryset.count()
            self.message_user(
                request, _("Successfully deleted %(count)d record/s.") % {
                    "count": n, }, messages.SUCCESS
            )

            return None
        else:

            opts = self.model._meta

            if len(queryset) == 1:
                objects_name = force_text(opts.verbose_name)
            else:
                objects_name = force_text(opts.verbose_name_plural)

            using = router.db_for_write(self.model)

            del_obj, model_c, perms_n, protected = get_deleted_objects(
                queryset, opts, request.user, self.admin_site, using
            )

            context = {
                'title': "",
                'delete_topic': [queryset],
                'ids': queryset.values_list("pk"),
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'opts': opts,
                'objects_name': objects_name,
                'deletable_objects': [del_obj],
                'action': 'delete_topic',
            }

            return TemplateResponse(
                request, 'muss/admin/confirm_delete.html', context
            )

    delete_topic.short_description = _(
        "Delete selected %(verbose_name_plural)s"
    )


class ForumAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'category', 'forum_description',
        'topics_count', 'is_moderate', 'get_moderators',
        'public_forum'
    )
    list_filter = ['name', 'category']
    search_fields = ['name']
    actions = ['delete_forum']

    def get_moderators(self, obj):
        return "\n".join([p.username for p in obj.moderators.all()])
    get_moderators.short_description = _("Moderators")

    def get_actions(self, request):
        actions = super(ForumAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_forum(self, request, queryset):
        """
        This method remove forum selected
        in the admin django. Can remove one
        o more records.
        """
        if not self.has_delete_permission(request):
            raise PermissionDenied

        if request.POST.get("post"):
            for obj in queryset:
                forum_id = obj.pk
                # Remove permissions to moderators
                obj.remove_user_permissions_moderator()

                # Delete record
                models.Forum.objects.filter(pk=forum_id).delete()

            n = queryset.count()
            self.message_user(
                request, _("Successfully deleted %(count)d record/s.") % {
                    "count": n, }, messages.SUCCESS
            )

            return None
        else:

            opts = self.model._meta

            if len(queryset) == 1:
                objects_name = force_text(opts.verbose_name)
            else:
                objects_name = force_text(opts.verbose_name_plural)

            using = router.db_for_write(self.model)

            del_obj, model_c, perms_n, protected = get_deleted_objects(
                queryset, opts, request.user, self.admin_site, using
            )

            context = {
                'title': "",
                'delete_topic': [queryset],
                'ids': queryset.values_list("pk"),
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'opts': opts,
                'objects_name': objects_name,
                'deletable_objects': [del_obj],
                'action': 'delete_forum'
            }

            return TemplateResponse(
                request, 'muss/admin/confirm_delete.html', context
            )

    delete_forum.short_description = _(
        "Delete selected %(verbose_name_plural)s"
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'topic', 'forum', 'date', 'user',
    )
    list_filter = ['topic', 'user']
    search_fields = ['topic', 'user']

    def forum(self, obj):
        return obj.topic.forum

    def save_model(self, request, obj, form, change):
        obj.save()
        topic = obj.topic

        # If is create
        if not change:
            # Send notifications comment
            params = nt.get_users_and_send_notification_comment(
                request.user, topic, obj
            )
            list_us = params['list_us']
            list_email = params['list_email']

            # Get url topic for email
            url = utils.get_url_topic(request, topic)

            # Send email
            nt_email.send_mail_comment(str(url), list_email)

            # Data necessary for realtime
            data = realtime.data_base_realtime(
                obj, topic.forum, False
            )

            # Send new notification realtime
            realtime.new_notification(data, list_us)

            # Send new comment in realtime
            comment_description = obj.description
            realtime.new_comment(data, comment_description)

    forum.short_description = _("Forum")
    forum.admin_order_field = 'topic__forum'


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site', 'logo',)
    form = forms.FormAdminConfiguration

    def has_delete_permission(self, request, obj=None):
        # Not delete record
        return False

    def has_add_permission(self, request):
        # Not add record
        return False


class MessageForumAdmin(admin.ModelAdmin):
    list_display = (
        'forum', 'message_information',
        'message_expires_from', 'message_expires_to'
    )


class RegisterAdmin(admin.ModelAdmin):
    list_display = (
        'forum', 'user', 'is_enabled',
    )


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'
    form = forms.FormAdminProfile


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name',)

    def has_delete_permission(self, request, obj=None):
        # Not delete record
        return False

    def has_add_permission(self, request):
        # Not add record
        return False


# Unregisters
admin.site.unregister(get_user_model())
admin.site.unregister(Theme)
admin.site.unregister(Site)

# Registers
admin.site.register(Site, SiteAdmin)
admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(models.Category)
admin.site.register(models.Register, RegisterAdmin)
admin.site.register(models.Forum, ForumAdmin)
admin.site.register(models.Topic, TopicAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Configuration, ConfigurationAdmin)
admin.site.register(models.MessageForum, MessageForumAdmin)
