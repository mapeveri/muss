import mistune

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework_json_api import serializers
from rest_framework_json_api.relations import (
    SerializerMethodResourceRelatedField
)

from muss import models, utils
from muss.api.fields import CustomFileField
from muss.validators import valid_extension_image


# Serializers Users
class UserSerializer(serializers.ModelSerializer):
    # For profile relation
    user = SerializerMethodResourceRelatedField(many=False, read_only=True)
    user_photo = serializers.SerializerMethodField()

    def get_user_photo(self, obj):
        """
        Get photo profile topic user
        """
        return utils.get_photo_profile(obj)

    def create(self, validated_data):
        User = get_user_model()

        # Check if exists the email
        user = User.objects.filter(email=validated_data['email'])
        if user:
            raise serializers.ValidationError(_("The email already exists."))

        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.is_active = False
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


# Serializers Categories
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


# Serializers Forum
class ForumSerializer(serializers.ModelSerializer):
    childs_forums = serializers.SerializerMethodField()
    parents_forums = serializers.SerializerMethodField()
    pending_moderations = serializers.SerializerMethodField()

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

    def get_parents_forums(self, obj):
        """
        Get forums parent of forum
        """
        forums = []
        if obj:
            if not(obj.parent is None):
                parents = models.Forum.objects.raw("""
                    with recursive forums_parents as (
                        select id, parent_id, name, slug
                            from muss_forum
                            where id = """ + str(obj.pk) + """
                        union all
                        select f.id, f.parent_id, f.name, f.slug
                            from muss_forum f
                            join forums_parents p on p.parent_id = f.id
                        )
                        select * from forums_parents
                        WHERE id <> """ + str(obj.pk) + """
                        ORDER BY id;"""
                    )

                for forum in parents:
                    forums.append({
                        'pk': forum.pk, 'slug': forum.slug,
                        'name': forum.name
                    })
        return forums

    def get_pending_moderations(self, obj):
        """
        Check if the forum has topic pending moderations
        """
        if obj.is_moderate:
            total = obj.forums.filter(is_moderate=False).count()
            if total > 0:
                return True
        return False

    class Meta:
        model = models.Forum
        fields = '__all__'


# Serializers Topic
class TopicSerializer(serializers.ModelSerializer):
    total_comments = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    forum = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    html_description = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    users_topic_comment = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        """
        Get total comments of topic
        """
        return obj.topics.count()

    def get_views(self, obj):
        """
        Get total hitcounts
        """
        hit = models.HitcountTopic.objects.filter(topic=obj)
        if hit.exists():
            count = len(hit.first().data)
        else:
            count = 0
        return count

    def get_html_description(self, obj):
        # Parse markdown
        return mistune.markdown(obj.description)

    def get_likes(self, obj):
        # Get likes topic
        try:
            likes = obj.likes_topic.users
        except models.LikeTopic.DoesNotExist:
            likes = []
        return likes

    def get_users_topic_comment(self, obj):
        # I get the users who participated in the topic
        users = []
        list_users = []
        username_topic = obj.user.username

        for comment in obj.topics.all():
            username = comment.user.username
            if not (username in list_users):
                photo = utils.get_photo_profile(comment.user.id)
                record = {
                    "username": username,
                    "photo": photo
                }
                # If is creator topic, add top
                if username == username_topic:
                    users.insert(0, record)
                else:
                    users.append(record)
                list_users.append(username)

        # If creator topic not exists, add
        if not (username_topic in list_users) and obj.topics.count() > 0:
            photo = utils.get_photo_profile(obj.user.id)
            users.insert(0, {
                "username": username_topic,
                "photo": photo
            })

        return users

    class Meta:
        model = models.Topic
        fields = '__all__'
        read_only_fields = ('slug', )


# Serializers register
class RegisterSerializer(serializers.ModelSerializer):
    forum = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = models.Register
        exclude = ('date',)


# Serializers comment
class CommentSerializer(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    html_description = serializers.SerializerMethodField()
    html_description = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    def get_html_description(self, obj):
        # Parse markdown
        return mistune.markdown(obj.description)

    def get_likes(self, obj):
        # Get likes comment
        try:
            likes = obj.likes_comment.users
        except models.LikeComment.DoesNotExist:
            likes = []
        return likes

    class Meta:
        model = models.Comment
        fields = '__all__'


# Serializers profile
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    photo = CustomFileField(
        validators=[valid_extension_image],
        max_length=None, allow_empty_file=True,
    )
    last_seen = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    def get_last_seen(self, obj):
        return obj.last_seen

    def get_online(self, obj):
        return obj.online

    class Meta:
        model = models.Profile
        fields = '__all__'


# Serializers Message Forum
class MessageForumSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MessageForum
        fields = '__all__'


# Serializers HitcountTopic
class HitcountTopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.HitcountTopic
        fields = '__all__'


# Serializers LikeTopic
class LikeTopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LikeTopic
        fields = '__all__'


# Serializers LikeComment
class LikeCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LikeComment
        fields = '__all__'


# Serializers Notification
class NotificationSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    def get_comment(self, obj):
        if str(obj.content_object._meta) == "muss.comment":
            return {
                'topicid': obj.content_object.topic.pk,
                'slug': obj.content_object.topic.slug,
                'title': obj.content_object.topic.title,
                'username': obj.content_object.user.username,
                'userid': obj.content_object.user.pk
            }
            return None

    def get_topic(self, obj):
        if str(obj.content_object._meta) == "muss.topic":
            return {
                'topicid': obj.content_object.pk,
                'slug': obj.content_object.slug,
                'title': obj.content_object.title,
                'username': obj.content_object.user.username,
                'userid': obj.content_object.user.pk
            }
        else:
            return None

    class Meta:
        model = models.Notification
        fields = '__all__'
