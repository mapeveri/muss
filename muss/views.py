import base64
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _

from muss import models, notifications_email as nt_email


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
            # Decoding username
            username = base64.b64decode(
                username.encode("utf-8")
            ).decode("ascii")
            # Parameters for template
            data = {
                'username': username, 
                'token': csrf_token,
                'SITE_NAME': settings.SITE_NAME
            }

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
        if request.user.is_authenticated:
            raise Http404

        username = request.POST.get('username')
        if username:
            User = get_user_model()
            user = get_object_or_404(User, username=username)
            email = user.email

            # For confirm email
            data = nt_email.get_data_confirm_email(email)

            # Update activation key
            profile = get_object_or_404(models.Profile, user=user)
            profile.activation_key = data['activation_key']
            profile.key_expires = data['key_expires']
            profile.save()

            # Send email for confirm user
            nt_email.send_welcome_email(
                email, username, data['activation_key']
            )

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
            User = get_user_model()
            user = get_object_or_404(User, email=email)

            subject_template_name = "muss/password_reset_subject.txt"
            email_template_name = "muss/password_reset_email.html"
            context = context = {
                'email': email,
                'domain': request.META['HTTP_HOST'],
                'site_name': settings.SITE_NAME,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            }
            from_email = None
            to_email = email

            nt_email.send_mail_reset_password(
                subject_template_name, email_template_name, context,
                from_email, to_email
            )

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
            User = get_user_model()
            try:
                # urlsafe_base64_decode() decodes to bytestring
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            token_generator = default_token_generator
            if user is not None and token_generator.check_token(user, token):
                # Is a valid link
                if valid_link:
                    return HttpResponse(200)

                password = request.POST.get('password')
                if password:
                    # Update password user
                    user.set_password(password)
                    user.save()
                else:
                    # Invalid form
                    message = str(_("Failed to reset password."))
                    return HttpResponse(json.dumps({
                        'status': 200, 'message': message
                    }))
            else:
                # Invalid link
                messages.error(request, _(
                    "The password reset link was invalid, "
                    "possibly because it has already been used. "
                    "Please request a new password reset."
                ))
                raise Http404

            return HttpResponse(json.dumps({'status': 200, 'message': ''}))
        else:
            raise Http404
