import base64

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from muss import models, utils


class IndexView(TemplateView):
    """
    Index app
    """
    template_name = "muss/index.html"


class ConfirmEmailView(View):
    """
    Form confirm email
    """
    template_name = "muss/confirm_email.html"

    def get(self, request):
        raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            raise Http404

        username = request.POST.get('username')
        activation_key = request.POST.get('activation_key')
        csrf_token = request.POST.get('csrfmiddlewaretoken')

        if username and activation_key and csrf_token and request.is_ajax():
            # Decoding username
            username = base64.b64decode(
                username.encode("utf-8")
            ).decode("ascii")
            # Parameters for template
            data = {'username': username, 'token': csrf_token}

            # Check if not expired key
            user_profile = get_object_or_404(
                models.Profile, activation_key=activation_key
            )

            if user_profile.key_expires < timezone.now():
                template = render_to_string(
                    "muss/confirm_email_expired.html", data)
                return HttpResponse(template)

            # Active user
            User = get_user_model()
            user = get_object_or_404(User, username=username)
            user.is_active = True
            user.save()
            template = render_to_string(self.template_name, data)
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
        if request.user.is_authenticated():
            raise Http404

        username = request.POST.get('username')
        if username:
            User = get_user_model()
            user = get_object_or_404(User, username=username)
            email = user.email

            # For confirm email
            data = utils.get_data_confirm_email(email)

            # Update activation key
            profile = get_object_or_404(models.Profile, user=user)
            profile.activation_key = data['activation_key']
            profile.key_expires = data['key_expires']
            profile.save()

            # Send email for confirm user
            utils.send_welcome_email(email, username, data['activation_key'])

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
        if request.user.is_authenticated():
            raise Http404

        email = request.POST.get('email')
        if email and request.is_ajax():
            pass
        else:
            raise Http404
