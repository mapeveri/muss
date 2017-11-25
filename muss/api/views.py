from django.db.models import F, Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchQuery, SearchVector
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

from muss import (
    models, notifications_email as nt_email,
    realtime, utils, notifications as nt
)
from muss.api import serializers, utils as utils_api
from muss.api.permissions import (
    CommentPermissions, TopicPermissions, IsReadOnly,
    RegisterPermissions
)
from muss.api.renderers import JSONRendererApiJson


# ViewSets for user
class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all().order_by("pk")
    serializer_class = serializers.UserSerializer
    resource_name = 'users'
    http_method_names = ['get', 'post']


# ViewSets for category
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
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
            queryset = utils_api.get_categories_forums()
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


# ViewSets for forum
class ForumViewSet(viewsets.ReadOnlyModelViewSet):
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


# ViewSets for topic
class TopicViewSet(viewsets.ModelViewSet):
    resource_name = 'topics'
    queryset = models.Topic.objects.all()
    serializer_class = serializers.TopicSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, TopicPermissions,
    )

    def get_queryset(self, *args, **kwargs):
        type_filter = self.request.GET.get('filter')
        pk = self.request.GET.get('pk')
        slug = self.request.GET.get('slug')
        search_title = self.request.GET.get('title')
        suggest = self.request.GET.get('suggest')
        username = self.request.GET.get('username')

        if type_filter == 'only_topic' and pk and slug:
            # Get only topic
            self.queryset = self.queryset.filter(
                pk=pk, slug=slug, is_moderate=True
            )
        elif type_filter == 'by_forum' and slug:
            # Filter topics by forum
            self.queryset = self.queryset.filter(
                forum__slug=slug, is_moderate=True
            )
        elif type_filter == 'search' and search_title:
            # Search topics
            self.queryset = self.queryset.annotate(
                search=SearchVector('title', 'description')
            ).filter(search=SearchQuery(search_title), is_moderate=True)

        elif type_filter == "by_user" and username:
            # Filter by user topic
            self.queryset = self.queryset.filter(
                user__username=username, is_moderate=True
            )
        elif type_filter == 'suggests' and suggest:
            # Filter suggest topic
            topic = get_object_or_404(
                models.Topic, pk=suggest, is_moderate=True
            )
            words = topic.title.split(" ")
            condition = Q()
            for word in words:
                condition |= Q(title__icontains=word)

            self.queryset = models.Topic.objects.filter(
                condition, Q(forum__pk=topic.forum_id, is_moderate=True)
            ).exclude(
                pk=topic.pk
            )[:10]

        return self.queryset

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated():
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(TopicViewSet, self).get_permissions()

    def perform_create(self, serializer):
        request = self.request
        forum_id = int(request.data['forum']['id'])
        user_id = int(request.data['user']['id'])

        # If is my user or is superuser can create
        if user_id == request.user.id or request.user.is_superuser:
            forum = get_object_or_404(models.Forum, pk=forum_id)
            user = get_object_or_404(get_user_model(), pk=request.user.id)

            category = forum.category.name
            # If has permissions
            if utils.user_can_create_topic(category, forum, request.user):
                # Save the record topic
                if serializer.is_valid():
                    # Check if moderation topic
                    is_moderate = utils.check_topic_moderate(
                        request.user, forum
                    )
                    # If the forum is moderate send email
                    serializer = utils.check_moderate_topic_email(
                        request, forum, serializer
                    )
                    # Save record
                    topic = serializer.save(
                        forum=forum, user=user, is_moderate=is_moderate
                    )
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # If is moderate send notifications
                if is_moderate:
                    domain = utils.get_domain(request)
                    # Send email to moderators
                    nt_email.send_notification_topic_to_moderators(
                        forum, topic, domain
                    )

                    # Get moderators forum and send notification
                    list_us = nt.get_moderators_and_send_notification_topic(
                        request, forum, topic
                    )

                    # Data necessary for realtime
                    data = realtime.data_base_realtime(
                        topic, forum, True
                    )

                    # Send new notification realtime
                    realtime.new_notification(data, list_us)

                    # Send new topic in forum
                    realtime.new_topic_forum(forum_id, data)

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                raise PermissionDenied({
                    "message": "You don't have permission to access"
                })
        else:
            raise PermissionDenied({
                    "message": "Not your user"
                })


# ViewSets for register
class RegisterViewSet(viewsets.ModelViewSet):
    resource_name = 'registers'
    queryset = models.Register.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, RegisterPermissions)
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated():
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
            self.queryset = self.queryset.filter(
                forum__pk=forum_id, user__pk=user_id
            )
        elif type_filter == "members" and forum:
            forum_id = int(forum)
            # Get register users
            forum = get_object_or_404(
                models.Forum, pk=forum_id, hidden=False
            )
            moderators = forum.moderators.all()
            # Get registers, exclude moderators
            self.queryset = forum.register_forums.filter(
                ~Q(user__in=moderators)
            )
        return self.queryset

    def create(self, request, **kwargs):
        user_id = int(request.data['user']['id'])
        is_my_user = user_id == request.user.id
        # If is my user or is superuser can create
        if is_my_user or request.user.is_superuser:
            forum_id = int(request.data['forum']['id'])
            exists_register = models.Register.objects.filter(
                forum_id=forum_id, user=request.user
            )

            # If the register not exists
            if exists_register.count() == 0:
                return super(RegisterViewSet, self).create(request, **kwargs)
            else:
                raise PermissionDenied({
                    "message": "You are already Registered"
                })
        else:
            raise PermissionDenied({
                    "message": "Not your user"
                })

    def perform_create(self, serializer):
        request = self.request
        forum_id = int(request.data['forum']['id'])
        forum = get_object_or_404(models.Forum, pk=forum_id)
        if serializer.is_valid():
            serializer.save(
                forum=forum, user=request.user
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


# ViewSets for comment
class CommentViewSet(viewsets.ModelViewSet):
    resource_name = 'comments'
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (CommentPermissions,)

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated():
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(CommentViewSet, self).get_permissions()

    def get_queryset(self, *args, **kwargs):
        topic = self.request.GET.get('topic')
        if topic:
            self.queryset = self.queryset.filter(topic__pk=topic)
        return self.queryset

    def perform_create(self, serializer):
        request = self.request
        # Get user id
        user_id = request.data['user']['id']

        # Get topic
        topic_id = request.data['topic']['id']
        topic = get_object_or_404(models.Topic, pk=topic_id)

        is_my_user = int(user_id) == request.user.id
        # If is my user or is superuser can create
        if is_my_user or request.user.is_superuser:
            # Save the record comment
            if serializer.is_valid():
                comment = serializer.save(
                    topic=topic, user=request.user
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Send notifications comment
            params = nt.get_users_and_send_notification_comment(
                request, topic, comment
            )
            list_us = params['list_us']
            list_email = params['list_email']

            # Get url for email
            url = url = utils.get_url_topic(request, topic)

            # Send email
            nt_email.send_mail_comment(str(url), list_email)

            # Data necessary for realtime
            data = realtime.data_base_realtime(
                comment, topic.forum, False
            )

            # Send new notification realtime
            realtime.new_notification(data, list_us)

            # Send new comment in realtime
            comment_description = request.data['description']
            realtime.new_comment(data, comment_description)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            raise PermissionDenied({
                    "message": "Error: User incorrect."
                })


# ViewSets for profile
class ProfileViewSet(viewsets.ModelViewSet):
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


# ViewSets for MessageForum
class MessageForumViewSet(viewsets.ReadOnlyModelViewSet):
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


# ViewSets for HitcountTopic
class HitcountTopicViewSet(viewsets.ModelViewSet):
    queryset = models.HitcountTopic.objects.all().order_by("pk")
    serializer_class = serializers.HitcountTopicSerializer
    http_method_names = ['get', 'post']

    def create(self, request):
        if request.session.session_key is None:
            request.session.save()

        topic_id = request.data['topic']
        session = request.session.session_key
        ip = request.META['REMOTE_ADDR']

        topic = get_object_or_404(models.Topic, pk=topic_id)
        hit = models.HitcountTopic.objects.filter(topic=topic)

        # Check if exists hitcount for topic
        if not hit.exists():
            # Create hitcout topic
            models.HitcountTopic.objects.create(
                topic=topic, data=[{'session': session, 'ip': ip}]
            )
            count = 1
        else:
            # Check if exists the session in the topic
            s = hit.filter(data__contains=[{'session': session, 'ip': ip}])
            if not s.exists():
                # Not exists, then i create the session
                record = hit.first()
                data = record.data
                # Insert new session to existing sessions
                data.append({'session': session, 'ip': ip})
                record.data = data
                # Update record in the field data
                record.save()
                count = len(data)
            else:
                count = len(hit.first().data)

        return Response({"success": True, "total": count})


class CheckPermissionsForumUserView(APIView):
    """
    Check the permissions that a user has in a forum
    """
    def get(self, request, format=None):
        response = {
            'register': False,
            'is_moderator': False,
            'is_troll': False,
        }

        # Parameters
        user_id = self.request.GET.get('user_id')
        forum_id = self.request.GET.get('forum_id')

        if user_id and forum_id:
            # Check if user is registered in the forum
            total_register = models.Register.objects.filter(
                user__pk=user_id, forum__pk=forum_id
            ).count()

            if total_register > 0:
                response['register'] = True

            # Check if user logged is moderator in the forum
            total_moderator = models.Forum.objects.filter(
                pk=forum_id, moderators__in=[user_id]
            ).count()

            if total_moderator > 0:
                response['is_moderator'] = True

            # Check if user logged is a troll
            profile = models.Profile.objects.filter(user__id=user_id)
            if profile.exists():
                response['is_troll'] = profile.first().is_troll

        return Response(response)


# Viewset for LikeTopic
class LikeTopicViewSet(viewsets.ModelViewSet):
    queryset = models.LikeTopic.objects.all().order_by("pk")
    serializer_class = serializers.LikeTopicSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        topic_pk = request.data['topic']
        user = int(request.data['users'])
        lt = models.LikeTopic.objects.filter(topic__pk=topic_pk)
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
                models.Topic.objects.filter(pk=topic_pk).update(
                    total_likes=F('total_likes') + 1
                )
        else:
            topic = models.Topic.objects.filter(pk=topic_pk)
            models.LikeTopic.objects.create(
                topic=topic.first(), users=[{'user': user}]
            )

            # Increment total like
            topic.update(
                total_likes=F('total_likes') + 1
            )

        return Response({'success': 'ok'})

    def destroy(self, request, pk=None):
        user_pk = int(request.data['users'])
        lt = models.LikeTopic.objects.filter(topic__pk=pk).first()
        users = lt.users

        for i, d in enumerate(users):
            if d['user'] == user_pk:
                users.pop(i)
                break

        lt.users = users
        lt.save()

        # Decrement like in total like
        models.Topic.objects.filter(pk=pk).update(
            total_likes=F('total_likes') - 1
        )

        return Response({'success': 'ok'})


# Viewset for LikeComment
class LikeCommentViewSet(viewsets.ModelViewSet):
    queryset = models.LikeComment.objects.all().order_by("pk")
    serializer_class = serializers.LikeCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        comment_pk = request.data['comment']
        user = int(request.data['users'])
        lc = models.LikeComment.objects.filter(comment__pk=comment_pk)
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
                models.Comment.objects.filter(pk=comment_pk).update(
                    total_likes=F('total_likes') + 1
                )
        else:
            comment = models.Comment.objects.filter(pk=comment_pk)
            models.LikeComment.objects.create(
                comment=comment.first(), users=[{'user': user}]
            )

            # Increment total like
            comment.update(
                total_likes=F('total_likes') + 1
            )

        return Response({'success': 'ok'})

    def destroy(self, request, pk=None):
        user_pk = int(request.data['users'])
        lc = models.LikeComment.objects.filter(comment__pk=pk).first()
        users = lc.users

        for i, d in enumerate(users):
            if d['user'] == user_pk:
                users.pop(i)
                break

        lc.users = users
        lc.save()

        # Decrement like in total like
        models.Comment.objects.filter(pk=pk).update(
            total_likes=F('total_likes') - 1
        )

        return Response({'success': 'ok'})


# ViewSets for user
class NotificationViewSet(viewsets.ModelViewSet):
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

        limit = self.request.GET.get('limit')
        if user_id == self.request.user.id:
            User = get_user_model()
            user = get_object_or_404(User, pk=user_id)
            if limit:
                return self.queryset.filter(
                    user=user
                ).order_by("-date")[:int(limit)]
            else:
                return self.queryset.filter(user=user).order_by("-date")
        else:
            raise Http404


class GetTotalPendingNotificationsUser(APIView):
    """
    Get total pending notification user
    """
    def get(self, request, format=None):
        # Parameters
        user_id = self.request.GET.get('user_id')
        if user_id:
            user_id = int(user_id)
            if user_id == self.request.user.id:
                User = get_user_model()
                user = get_object_or_404(User, pk=user_id)
                total = models.Notification.objects.filter(
                    user=user, is_seen=False
                ).count()

                return Response({"total": total})
            else:
                raise Http404
        else:
            raise Http404


class UpdateSeenNotifications(APIView):
    """
    Update is_seen property in notification by user
    """
    def post(self, request, format=None):
        user_id = self.request.POST.get('user_id')
        if user_id:
            user_id = int(user_id)
            if user_id == self.request.user.id:
                models.Notification.objects.filter(
                    user=request.user
                ).update(is_seen=True)
                return Response({"success": True})
            else:
                raise Http404
        else:
            raise Http404


class UploadsView(APIView):
    """
    Upload files in editor
    """
    def post(self, request, format=None):
        urls = []
        if request.user.is_authenticated():
            for file_name in self.request.FILES:
                file = self.request.FILES[file_name]
                r = models.Upload.objects.create(
                    user=request.user, attachment=file
                )
                domain = utils.get_domain(request)
                url = domain + settings.MEDIA_URL + r.attachment.name
                urls.append(url)
        return Response({"success": True, "urls": urls})
