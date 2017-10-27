from django.conf.urls import url
from rest_framework import routers
from muss.api import views


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
# Get users endpoint
router.register(r'users', views.UserViewSet)
# Get categories
router.register(r'categories', views.CategoryViewSet)
# Get forums endpoint
router.register(r'forums', views.ForumViewSet)
# Get topics endpoint
router.register(r'topics', views.TopicViewSet)
# Get register endpoint
router.register(r'registers', views.RegisterViewSet)
# Get comments endpoint
router.register(r'comments', views.CommentViewSet)
# Get profiles endpoint
router.register(r'profiles', views.ProfileViewSet)
# Get message forum
router.register(r'messageforums', views.MessageForumViewSet)
# Hitcount topic
router.register(r'hitcounts', views.HitcountTopicViewSet)
# Like comment endpoint
router.register(r'likecomments', views.LikeCommentViewSet)
# Like topic endpoint
router.register(r'liketopics', views.LikeTopicViewSet)
# Notifications endpoint
router.register(r'notifications', views.NotificationViewSet)


urlpatterns = [
    # Get permissions of the forum for user
    url(r'^check-permissions-forum-user/$',
        views.CheckPermissionsForumUserView.as_view()),
    # Get total notifications pending by user
    url(r'^get-total-pending-notifications-user/$',
        views.GetTotalPendingNotificationsUser.as_view()),
    # Update is_seen property in notification by user
    url(r'^update-seen-notifications-user/$',
        views.UpdateSeenNotifications.as_view()),
    # Uploads files
    url(r'^uploads/$', views.UploadsView.as_view()),
]
