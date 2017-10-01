from rest_framework import permissions
from muss import models, utils


class IsReadOnly(permissions.BasePermission):
    """
    Readonly permissions.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


class TopicPermissions(permissions.BasePermission):
    """
    Check if is superuser or moderator or creator
    of topic for can crete, remove, etc.
    """
    def check_permissions_topic(self, request, forum, user):
        if forum:
            category = forum.category.name
        else:
            forum = None
            category = None

        # Get if is moderator
        is_moderator = utils.is_user_moderator_forum(
            category, forum, request.user
        )

        # Only allow if is superuser or moderator or cretor of topic
        return (
            request.user.is_superuser or
            is_moderator or
            user == request.user.id
        )

    def has_permission(self, request, view):
        if request.method == 'POST':
            try:
                # To create
                forum_id = int(request.data['forum']['id'])
                user_id = int(request.data['user']['id'])
                forum = models.Forum.objects.filter(pk=forum_id).first()

                return self.check_permissions_topic(
                    request, forum, user_id
                )
            except KeyError:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # Allow get requests for all
        if request.method == 'GET':
            return True
        else:
            # To delelete
            return self.check_permissions_topic(
                request, obj.forum, obj.user.id
            )


class RegisterPermissions(TopicPermissions):
    """
    Check if is superuser or moderator or creator
    of register for can crete, remove, etc.
    """
    pass


class CommentPermissions(permissions.BasePermission):
    """
    Check if is superuser or moderator or creator
    of comment for can crete, remove, etc.
    """
    def check_permissions_comment(self, request, topic, user):
        if topic:
            forum = topic.forum
            category = topic.forum.category.name
        else:
            forum = None
            category = None

        # Get if is moderator
        is_moderator = utils.is_user_moderator_forum(
            category, forum, request.user
        )

        # Only allow if is superuser or moderator or cretor of comment
        return (
            request.user.is_superuser or
            is_moderator or
            user == request.user.id
        )

    def has_permission(self, request, view):
        if request.method == 'POST':
            try:
                # To create
                topic_id = int(request.data['topic']['id'])
                user_id = int(request.data['user']['id'])
                topic = models.Topic.objects.filter(pk=topic_id).first()

                return self.check_permissions_comment(
                    request, topic, user_id
                )
            except KeyError:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # Allow get requests for all
        if request.method == 'GET':
            return True
        else:
            # To delelete
            return self.check_permissions_comment(
                request, obj.topic, obj.user.id
            )
