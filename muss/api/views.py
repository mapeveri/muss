from django.db.models import F, Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from muss import models, notification_email as nt_email, realtime, utils
from muss.api import serializers, utils as utils_api
from muss.api.permissions import (
    CommentPermissions, TopicPermissions, IsReadOnly,
    RegisterPermissions
)
from muss.api.renderers import JSONRendererApiJson


# ViewSets for user
class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    resource_name = 'users'


# ViewSets for category
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_renderers(self):
        type_filter = self.request.GET.get('filter')
        if type_filter == 'forums':
            if settings.DEBUG:
                renderers_classes = (JSONRendererApiJson, BrowsableAPIRenderer,)
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
        pk = self.request.GET.get('pk')
        slug = self.request.GET.get('slug')

        if pk and slug:
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

        if type_filter == 'only_topic' and pk and slug:
            # Get only topic
            self.queryset = self.queryset.filter(pk=pk, slug=slug)
        elif type_filter == 'by_forum' and slug:
            # Filter topics by forum
            self.queryset = self.queryset.filter(forum__slug=slug)
        elif type_filter == 'search' and search_title:
            # Search topics
            self.queryset = self.queryset.filter(
                title__icontains=search_title, is_moderate=True
            )
        elif type_filter == 'suggests' and suggest:
            # Filter suggest topic
            topic = get_object_or_404(models.Topic, pk=suggest)
            words = topic.title.split(" ")
            condition = Q()
            for word in words:
                condition |= Q(title__icontains=word)

            self.queryset = models.Topic.objects.filter(
                condition, Q(forum__pk=topic.forum_id)
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
        is_my_user = int(request.data['user']) == request.user.id

        # If is my user or is superuser can create
        if is_my_user or request.user.is_superuser:
            forum_id = request.data['forum']
            forum = get_object_or_404(models.Forum, pk=forum_id)
            category = forum.category.name
            # If has permissions
            if utils.user_can_create_topic(category, forum, request.user):
                # Save the record topic
                if serializer.is_valid():
                    # If the forum is moderate send email
                    serializer = utils.check_moderate_topic_email(
                        request, forum, serializer
                    )
                    # Save record
                    topic = serializer.save()
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Parameters for realtime
                photo = utils.get_photo_profile(request.user)
                username = request.user.username
                forum_name = forum.name

                # Get moderators forum and send notification
                list_us = utils.get_moderators_and_send_notification_topic(
                    request, forum, topic
                )

                # Data necessary for realtime
                data = realtime.data_base_realtime(
                    topic, photo, forum_name, username
                )
                data['is_topic'] = True
                data['is_comment'] = False

                # Send new notification realtime
                realtime.new_notification(data, list_us)

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
    queryset = models.Register.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, RegisterPermissions)

    def get_permissions(self):
        # If is troll then only is read only
        if self.request.user.is_authenticated():
            if self.request.user.user.is_troll:
                self.permission_classes = [IsReadOnly, ]
        return super(RegisterViewSet, self).get_permissions()

    def create(self, request, **kwargs):
        is_my_user = int(request.data['user']) == request.user.id
        # If is my user or is superuser can create
        if is_my_user or request.user.is_superuser:
            forum_id = request.data['forum']
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

    def create(self, request):
        topic_id = request.data['topic']
        request.data['topic'] = topic_id['id']

        user_id = request.data['user']
        request.data['user'] = user_id['id']

        return super(CommentViewSet, self).create(request)

    def perform_create(self, serializer):
        request = self.request
        is_my_user = int(request.data['user']) == request.user.id
        # If is my user or is superuser can create
        if is_my_user or request.user.is_superuser:
            # Save the record comment
            if serializer.is_valid():
                comment = serializer.save()
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get topic
            topic_id = request.data['topic']
            topic = get_object_or_404(models.Topic, pk=topic_id)

            # Parameters for notification comments
            photo = utils.get_photo_profile(request.user)
            username = request.user.username
            forum = topic.forum.name

            # Send notifications comment
            params = utils.get_users_and_send_notification_comment(
                request, topic, comment
            )
            list_us = params['list_us']
            list_email = params['list_email']

            # Get url for email
            url = ""
            url += utils.get_domain(request)
            url += "/topic/" + str(topic.pk) + "/" + topic.slug + "/"

            # Send e    mail
            nt_email.send_mail_comment(str(url), list_email)

            # Data necessary for realtime
            data = realtime.data_base_realtime(topic, photo, forum, username)
            data['is_topic'] = False
            data['is_comment'] = True

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
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer


# ViewSets for MessageForum
class MessageForumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.MessageForum.objects.all()
    serializer_class = serializers.MessageForumSerializer


# ViewSets for HitcountTopic
class HitcountTopicViewSet(viewsets.ModelViewSet):
    queryset = models.HitcountTopic.objects.all()
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
                moderators__in=[user_id]
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
    queryset = models.LikeTopic.objects.all()
    serializer_class = serializers.LikeTopicSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self, *arg, **kwargs):
        type_filter = self.request.GET.get('filter')

        # Check if exists like in topic
        if type_filter == 'check_like_exists':
            user = self.request.GET.get('user')
            topic = self.request.GET.get('topic')

            lt = self.queryset.filter(topic__pk=topic)
            if lt.exists():
                exists = lt.filter(users__contains=[{'user': user}])
                if exists:
                    self.queryset = lt
                else:
                    self.queryset = models.LikeTopic.objects.none()
            else:
                self.queryset = models.LikeTopic.objects.none()

        return self.queryset

    def create(self, request):
        topic_pk = request.data['topic']
        user = request.data['users']
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
        user_pk = request.data['users']
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
    queryset = models.LikeComment.objects.all()
    serializer_class = serializers.LikeCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self, *arg, **kwargs):
        type_filter = self.request.GET.get('filter')

        # Check if exists like in comment
        if type_filter == 'check_like_exists':
            user = self.request.GET.get('user')
            comment = self.request.GET.get('comment')

            lc = self.queryset.filter(comment__pk=comment)
            if lc.exists():
                exists = lc.filter(users__contains=[{'user': user}])
                if exists:
                    self.queryset = lc
                else:
                    self.queryset = models.LikeComment.objects.none()
            else:
                self.queryset = models.LikeComment.objects.none()

        return self.queryset

    def create(self, request):
        comment_pk = request.data['comment']
        user = request.data['users']
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
        user_pk = request.data['users']
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
