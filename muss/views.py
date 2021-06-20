import json

from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.utils.translation import ugettext_lazy as _

from muss.services.auth import (
    confirm_email, new_key_activation,
    reset_password, reset_password_confirm
)


class IndexView(TemplateView):
    """
    Index app
    """
    template_name = "muss/base_muss.html"


class ConfirmEmailView(View):
    """
    Form confirm email
    """
    template_name = "muss/confirm_email.html"

    def get(self, request):
        raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        username = request.POST.get('username')
        activation_key = request.POST.get('activation_key')
        csrf_token = request.POST.get('csrfmiddlewaretoken')

        if username and activation_key and csrf_token and request.is_ajax():
            template = confirm_email(
                username, csrf_token, activation_key, self.template_name)
            return HttpResponse(template)
        else:
            raise Http404


class NewKeyActivationView(View):
    """
    View for get a new key activation
    """
    template_name = "muss/confirm_email_expired.html"

    def get(self, request):
        raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        username = request.POST.get('username')
        if username:
            new_key_activation(username)
            messages.success(request, _("Please, check your email."))
            return redirect("/")
        else:
            raise Http404


class ResetPasswordView(View):
    """
    View for reset password
    """

    def get(self, request):
        raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        email = request.POST.get('email')
        if email and request.is_ajax():
            reset_password(email, request.META['HTTP_HOST'],
                           request.is_secure())
            return HttpResponse(200)
        else:
            raise Http404


class PasswordResetConfirmView(View):
    """
    View for password reset confirm
    """

    def get(self, request, uidb64, token):
        raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        uidb64 = request.POST.get('uidb64')
        token = request.POST.get('token')
        valid_link = int(request.POST.get('valid_link'))

        assert uidb64 is not None and token is not None
        if request.is_ajax():
            password = request.POST.get('password')
            data = reset_password_confirm(
                uidb64, token, password, valid_link)

            if data['status'] == 404:
                messages.error(request, data['message'])
                raise Http404

            return HttpResponse(json.dumps({'status': 200, 'message': data['message']}))
        else:
            raise Http404
