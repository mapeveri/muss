from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from muss import models, utils
from muss.api import serializers
from muss.api.permissions import (
    CommentPermissions, TopicPermissions, IsReadOnly,
    RegisterPermissions
)
from muss.api.renderers import JSONRendererApiJson
from muss.services.category import get_categories_forums
from muss.services.comment import create_comment
from muss.services.hitcount_topic import create_hitcount_topic
from muss.services.like import (
    create_like_comment, delete_like_comment,
    create_like_topic, delete_like_topic
)
from muss.services.register_forum import (
    get_all_registers, get_register_by_members, create_register
)
from muss.services.topic import create_topic, filter_topic_by_filter
from muss.services.user.forum import (
    check_permissions_forum_user, get_forums_by_user
)
from muss.services.user.topic import user_can_create_topic


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSets for user
    """
    User = get_user_model()
    queryset = User.objects.all().order_by("pk")
    serializer_class = serializers.UserSerializer
    resource_name = 'users'
    http_method_names = ['get', 'post']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSets for category
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_renderers(self):
        type_filter = self.request.GET.get('filter')
        if type_filter == 'forums':
            if settings.DEBUG:
                renderers_classes = (
                    JSONRendererApiJson, BrowsableAPIRenderer,
                )
            else:
                renderers_classes = (JSONRendererApiJson,)
            self.renderer_classes = renderers_classes

        return [renderer() for renderer in self.renderer_classes]

    def list(self, request, *args, **kwargs):
        type_filter = self.request.GET.get('filter')

        if type_filter == 'forums':
            # Get list with categories and forums
            queryset = get_categories_forums()
            page = self.paginate_queryset(queryset)

            if page is not None:
                queryset_page = self.get_paginated_response(page)
                data = queryset_page.__dict__
                queryset = data['data']

                return Response({
                    'data': queryset['results'], 'meta': queryset['meta'],
                    'links': queryset['links']
                })

            return Response({'data': queryset})
        else:
            response = super(CategoryViewSet, self).list(
                request, *args, **kwargs
            )
            return response


class ForumViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSets for forum
    """
    queryset = models.Forum.objects.all()
    serializer_class = serializers.ForumSerializer

    def get_queryset(self, *args, **kwargs):
        type_filter = self.request.GET.get('filter')
        pk = self.request.GET.get('pk')
        slug = self.request.GET.get('slug')

        if pk and slug and type_filter == "only":
            # Get only forum
            self.queryset = self.queryset.filter(pk=pk, slug=slug)

        return self.queryset


class TopicViewSet(viewsets.ModelViewSet):
    """
    ViewSets for topic
    """
    resource_name = 'topics'
    queryset = models.Topic.objects.all()
    serializer_class = serializers.TopicSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, TopicPermissions,
    )

    def get_queryset(self, *args, **kwargs):
        return filter_topic_by_filter(self.request.GET, self.queryset)

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated:
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(TopicViewSet, self).get_permissions()

    def perform_create(self, serializer):
        request = self.request
        forum_id = int(request.data['forum']['id'])
        user_id = int(request.data['user']['id'])

        # If is my user or is superuser can create
        if user_id != request.user.id and not request.user.is_superuser:
            raise PermissionDenied({
                "message": "The user is invalid"
            })

        forum = get_object_or_404(models.Forum, pk=forum_id)
        user = get_object_or_404(get_user_model(), pk=request.user.id)
        category = forum.category.name

        # If has permissions
        if not user_can_create_topic(category, forum, request.user):
            raise PermissionDenied({
                "message": "You don't have permission to access"
            })

        # Save the record topic
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        domain = utils.get_domain(request)
        create_topic(request.user, forum, serializer, domain)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


class RegisterViewSet(viewsets.ModelViewSet):
    """
    ViewSets for register
    """
    resource_name = 'registers'
    queryset = models.Register.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, RegisterPermissions)
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated:
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(RegisterViewSet, self).get_permissions()

    def get_queryset(self, *args, **kwargs):
        type_filter = self.request.GET.get('filter')
        user = self.request.GET.get('user')
        forum = self.request.GET.get('forum')

        if forum and user and type_filter == "get_register":
            user_id = int(user)
            forum_id = int(forum)
            self.queryset = get_all_registers(user, forum, self.queryset)

        elif type_filter == "members" and forum:
            self.queryset = get_register_by_members(forum)

        return self.queryset

    def create(self, request, **kwargs):
        user_id = int(request.data['user']['id'])
        is_my_user = user_id == request.user.id

        # If is my user or is superuser can create
        if not is_my_user and not request.user.is_superuser:
            raise PermissionDenied({
                "message": "The user is invalid"
            })

        forum_id = int(request.data['forum']['id'])

        # Check if the forum is public or not
        forum = get_object_or_404(models.Forum, pk=forum_id)
        if forum.public_forum or request.user.is_superuser:
            request.data['is_enable'] = True
        else:
            request.data['is_enable'] = False

            # If the register not exists
            if create_register(forum, request.user) > 0:
                raise PermissionDenied({
                    "message": "You are already Registered"
                })

        return super(RegisterViewSet, self).create(request, **kwargs)

    def perform_create(self, serializer):
        request = self.request
        forum_id = int(request.data['forum']['id'])
        forum = get_object_or_404(models.Forum, pk=forum_id)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(forum=forum, user=request.user)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSets for comment
    """
    resource_name = 'comments'
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (CommentPermissions,)

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated:
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(CommentViewSet, self).get_permissions()

    def get_queryset(self, *args, **kwargs):
        topic = self.request.GET.get('topic')
        if topic:
            self.queryset = self.queryset.filter(topic__pk=topic)

        return self.queryset

    def perform_create(self, serializer):
        # Get user id
        user_id = self.request.data['user']['id']
        # Get topic
        topic_id = self.request.data['topic']['id']
        topic = get_object_or_404(models.Topic, pk=topic_id)

        is_my_user = int(user_id) == self.request.user.id
        # If is my user or is superuser can create
        if not is_my_user and not self.request.user.is_superuser:
            raise PermissionDenied({
                "message": "Error: User incorrect."
            })

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get url for email
        url = utils.get_url_topic(self.request, topic)

        # Save comment
        create_comment(self.request.user, serializer, topic, url)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSets for profile
    """
    resource_name = 'profiles'
    queryset = models.Profile.objects.all().order_by("pk")
    serializer_class = serializers.ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'patch']

    def get_queryset(self, *args, **kwargs):
        type_filter = self.request.GET.get('filter')
        username = self.request.GET.get('username')

        if type_filter == "get_profile_username" and username:
            self.queryset = self.queryset.filter(user__username=username)
        return self.queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Update receive_emails if is string from request
        r_emails = request.data.get('receive-emails')
        if isinstance(r_emails, str):
            receive_emails = True if r_emails == 'true' else False
            instance.receive_emails = receive_emails

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class MessageForumViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSets for MessageForum
    """
    queryset = models.MessageForum.objects.all().order_by("pk")
    serializer_class = serializers.MessageForumSerializer
    http_method_names = ['get']

    def get_queryset(self, *args, **kwargs):
        forum_id = self.request.GET.get('forum')
        if forum_id:
            forum_id = int(forum_id)
            now = timezone.now()
            self.queryset = self.queryset.filter(
                Q(forum__pk=forum_id),
                Q(message_expires_from__lte=now, message_expires_to__gte=now)
            )
        else:
            raise Http404

        return self.queryset


class HitcountTopicViewSet(viewsets.ModelViewSet):
    """
    ViewSets for HitcountTopic
    """
    queryset = models.HitcountTopic.objects.all().order_by("pk")
    serializer_class = serializers.HitcountTopicSerializer
    http_method_names = ['get', 'post']

    def create(self, request):
        if request.session.session_key is None:
            request.session.save()

        try:
            topic_id = request.data['topic']
        except KeyError:
            raise Http404

        session = request.session.session_key
        ip = request.META['REMOTE_ADDR']
        count = create_hitcount_topic(topic_id, session, ip)

        return Response({"success": True, "total": count})


class CheckPermissionsForumUserView(APIView):
    """
    Check the permissions that a user has in a forum private
    """

    def get(self, request, format=None):
        # Parameters
        user_id = self.request.GET.get('user_id')
        forum_id = self.request.GET.get('forum_id')

        if not user_id or not forum_id:
            raise Http404

        response = check_permissions_forum_user(user_id, forum_id)
        return Response(response)


class LikeTopicViewSet(viewsets.ModelViewSet):
    """
    Viewset for LikeTopic
    """
    queryset = models.LikeTopic.objects.all().order_by("pk")
    serializer_class = serializers.LikeTopicSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        try:
            topic_pk = request.data['topic']
            user = int(request.data['users'])
        except KeyError:
            raise Http404

        create_like_topic(user, topic_pk)
        return Response({'success': 'ok'})

    def destroy(self, request, pk=None):
        try:
            user_pk = int(request.data['users'])
        except KeyError:
            raise Http404

        delete_like_topic(pk, user_pk)

        return Response({'success': 'ok'})


class LikeCommentViewSet(viewsets.ModelViewSet):
    """
    Viewset for LikeComment
    """
    queryset = models.LikeComment.objects.all().order_by("pk")
    serializer_class = serializers.LikeCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        try:
            comment_pk = request.data['comment']
            user = int(request.data['users'])
        except KeyError:
            raise Http404

        create_like_comment(user, comment_pk)
        return Response({'success': 'ok'})

    def destroy(self, request, pk=None):
        try:
            user_pk = int(request.data['users'])
        except KeyError:
            raise Http404

        delete_like_comment(pk, user_pk)
        return Response({'success': 'ok'})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSets for user
    """
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    resource_name = 'notifications'
    http_method_names = ['get', 'post']

    def get_queryset(self, *args, **kwargs):
        try:
            user_id = int(self.request.GET.get('user'))
        except TypeError:
            user_id = None

        if not self.request.user.is_authenticated:
            raise Http404

        if user_id != self.request.user.id:
            raise Http404

        User = get_user_model()
        user = get_object_or_404(User, pk=user_id)
        limit = self.request.GET.get('limit')

        if limit:
            return self.queryset.filter(
                user=user
            ).order_by("-date")[:int(limit)]
        else:
            return self.queryset.filter(user=user).order_by("-date")


class GetTotalPendingNotificationsUser(APIView):
    """
    Get total pending notification user
    """

    def get(self, request, format=None):
        # Parameters
        user_id = self.request.GET.get('user_id')
        if not user_id:
            raise Http404

        user_id = int(user_id)
        if not self.request.user.is_authenticated:
            raise Http404

        if user_id != self.request.user.id:
            raise Http404

        User = get_user_model()
        user = get_object_or_404(User, pk=user_id)
        total = models.Notification.objects.filter(
            user=user, is_seen=False
        ).count()

        return Response({"total": total})


class UpdateSeenNotifications(APIView):
    """
    Update is_seen property in notification by user
    """

    def post(self, request, format=None):
        user_id = self.request.POST.get('user_id')
        if not user_id:
            raise Http404

        user_id = int(user_id)
        if not self.request.user.is_authenticated:
            raise Http404

        if user_id != self.request.user.id:
            raise Http404

        models.Notification.objects.filter(
            user=request.user
        ).update(is_seen=True)

        return Response({"success": True})


class UploadsView(APIView):
    """
    Upload files in editor
    """

    def post(self, request, format=None):
        urls = []
        if request.user.is_authenticated:
            for file_name in self.request.FILES:
                file = self.request.FILES[file_name]
                r = models.Upload.objects.create(
                    user=request.user, attachment=file
                )
                domain = utils.get_domain(request)
                url = domain + settings.MEDIA_URL + r.attachment.name
                urls.append(url)

        return Response({"success": True, "urls": urls})


class GetForumsByUser(APIView):
    """
    Get forums member user
    """

    def get(self, request, format=None):
        # Parameters
        username = self.request.GET.get('username')
        if not username:
            raise Http404

        list_forums = get_forums_by_user(username)
        return Response({"forums": list_forums})
