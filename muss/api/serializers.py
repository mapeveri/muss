from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework import serializers
from muss import models, utils


# Serializers Users
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'is_superuser', 'first_name', 'last_name',
            'email', 'is_staff', 'is_active', 'date_joined'
        )


# Serializers Categories
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


# Serializers Forum
class ForumSerializer(serializers.ModelSerializer):
    childs_forums = serializers.SerializerMethodField()
    parent_forums = serializers.SerializerMethodField()

    def get_childs_forums(self, obj):
        """
        Get forums childs of forum
        """
        forums = []
        for forum in obj.parents.all():
            forums.append({
                'pk': forum.pk, 'slug': forum.slug,
                'name': forum.name
            })
        return forums

    def get_parent_forums(self, obj):
        """
        Get forums parent of forum
        """
        forums = []
        if obj:
            if not(obj.parent is None):
                forums.append({
                    'pk': obj.parent.pk, 'slug': obj.parent.slug,
                    'name': obj.parent.name
                })
        return forums

    class Meta:
        model = models.Forum
        fields = '__all__'


# Serializers Topic
class TopicSerializer(serializers.ModelSerializer):
    total_comments = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        """
        Get total comments of topic
        """
        return models.Comment.objects.filter(topic__pk=obj.pk).count()

    def get_user_photo(self, obj):
        """
        Get photo profile topic user
        """
        return utils.get_photo_profile(obj.user)

    def get_username(self, obj):
        """
        Get username of topic user
        """
        return obj.user.username

    class Meta:
        model = models.Topic
        fields = '__all__'


# Serializers register
class RegisterSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(RegisterSerializer, self).__init__(*args, **kwargs)
        user = self.context['request'].user
        # If no is superuser, get forum that
        # not is register or not is moderator
        if not user.is_superuser and user.is_authenticated():
            registers = models.Register.objects.filter(user=user)
            self.fields['forum'].queryset = models.Forum.objects.filter(
                ~Q(moderators__in=[user.id]), ~Q(
                    register_forums__in=registers
                )
            )

            # Only my user
            User = get_user_model()
            self.fields['user'].queryset = User.objects.filter(id=user.id)

    class Meta:
        model = models.Register
        exclude = ('date',)


# Serializers comment
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args, **kwargs)
        user = self.context['request'].user
        if not user.is_superuser and user.is_authenticated():
            # Only my user
            User = get_user_model()
            self.fields['user'].queryset = User.objects.filter(id=user.id)

            # Topic not is close and is moderate not show
            self.fields['topic'].queryset = models.Topic.objects.filter(
                is_close=False, moderate=True
            )

    def get_username(self, obj):
        """
        Get username comment user
        """
        return obj.user.username

    def get_user_photo(self, obj):
        """
        Get photo profile comment user
        """
        return utils.get_photo_profile(obj.user)

    class Meta:
        model = models.Comment
        fields = '__all__'


# Serializers profile
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = '__all__'


# Serializers Message Forum
class MessageForumSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MessageForum
        fields = '__all__'
