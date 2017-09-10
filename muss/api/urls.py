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
router.register(r'messages-forums', views.MessageForumViewSet)
