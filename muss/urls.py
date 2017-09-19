from django.conf.urls import include, url

from rest_framework_jwt import views as jwt_views

from muss import views
from muss.feeds import TopicFeed
from muss.api.urls import router


urlpatterns = [
    # Url for django-rest-framework
    url(r'^api/', include(router.urls)),
    # Authentication routes
    url(r'^api/token-auth/', jwt_views.obtain_jwt_token),
    url(r'^api/token-refresh/', jwt_views.refresh_jwt_token),
    url(r'^api/verify-token/', jwt_views.verify_jwt_token),
    # Url's muss
    url(r'^feed/(?P<pk>\d+)/(?P<forum>.+)/$', TopicFeed(), name='rss'),
    # For ember-app
    url(r'^(?:.*)/?$', views.IndexView.as_view(), name='index'),
    # url(r'^login/', views.LoginView.as_view(), name='login'),
    # url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    # url(r'^join/', views.SignUpView.as_view(), name='signup'),
    # url(r'^confirm_email/(?P<username>.+)/(?P<activation_key>\w+)',
    #    views.ConfirmEmailView.as_view(), name='config_email'),
    # url(r'^new_key_activation/(?P<username>.+)',
    #    views.NewKeyActivationView.as_view(), name='new_key_activation'),
    # url(r'^reset_password/$', views.reset_password, name='password_reset'),
    # url(
    #     r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     views.reset_pass_confirm, name='password_reset_confirm'
    # ),
    # url(r'^reset/done/$', views.reset_done_pass,
    #    name='password_reset_complete'),
]
