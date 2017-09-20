from django.conf.urls import include, url

from rest_framework_jwt import views as jwt_views

from muss import views
from muss.feeds import TopicFeed
from muss.api.urls import router


urlpatterns = [
    # Url for django-rest-framework
    url(r'^api/', include(router.urls)),
    # Authentication routes jwt
    url(r'^api/token-auth/', jwt_views.obtain_jwt_token),
    # Url's muss
    url(r'^feed/(?P<pk>\d+)/(?P<forum>.+)/$', TopicFeed(), name='rss'),
    # For ember-app
    url(r'^(?:.*)/?$', views.IndexView.as_view(), name='index'),
]
