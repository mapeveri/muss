from django.conf.urls import include, url

from rest_framework_jwt import views as jwt_views

from muss import views
from muss.feeds import TopicFeed
from muss.api.urls import router


urlpatterns = [
    # Url for django-rest-framework
    url(r'^api/', include(router.urls)),
    url(r'^api/', include('muss.api.urls')),
    # Authentication route jwt
    url(r'^api/token-auth/', jwt_views.obtain_jwt_token),
    # Authentication routes
    url(r'^confirm-email/$', views.ConfirmEmailView.as_view(),
        name='confirm_email'),
    url(r'^new_key_activation/', views.NewKeyActivationView.as_view(),
        name='new_key_activation'),
    url(r'^reset-password/$', views.ResetPasswordView.as_view(),
        name='reset_password'),
    url(
        r'^reset/$', views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    # Url's muss
    url(r'^feed/(?P<pk>\d+)/(?P<forum>.+)/$', TopicFeed(), name='rss'),
    # For ember-app
    url(r'^(?:.*)/?$', views.IndexView.as_view(), name='index'),
]
