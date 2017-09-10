import base64

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    password_reset, password_reset_complete,
    password_reset_confirm
)
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from muss import forms, models, utils


class IndexView(TemplateView):
    """
    Index app
    """
    template_name = "muss/index.html"


class LoginView(FormView):
    """
    Login View
    """
    template_name = "muss/login.html"
    form_class = forms.FormLogin
    success_url = reverse_lazy("forums")

    def get(self, request, *args, **kwargs):
        data = {
            'form': self.form_class
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # Check if is authenticated and form valid
        if not request.user.is_authenticated():
            if form.is_valid():
                # This method is one method of class
                # FormLogin in forms.py and is the
                # responsible of authenticate to user
                user = form.form_authenticate()
                if user:
                    if user.is_active:
                        # Login is correct
                        login(request, user)
                        return redirect("forums")
                    else:
                        messages.error(request, _("The user is not active"))
                        return self.form_invalid(form, **kwargs)
                else:
                    return self.form_invalid(form, **kwargs)
            else:
                return self.form_invalid(form, **kwargs)
        else:
            return redirect("forums")


class LogoutView(View):
    """
    View logout
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)

        return redirect("forums")


class SignUpView(FormView):
    """
    This view is responsible of
    create one new user
    """
    template_name = "muss/signup.html"
    form_class = forms.FormSignUp
    success_url = reverse_lazy("signup")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect("forums")
        else:
            data = {'form': self.form_class}
            return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if not request.user.is_authenticated():
            if form.is_valid():
                form.create_user()
                msj = _(
                    "Registration was successful. Please, check your email "
                    "to validate the account."
                )
                messages.success(request, msj)
                return self.form_valid(form, **kwargs)
            else:
                messages.error(request, _("Invalid form"))
                return self.form_invalid(form, **kwargs)
        else:
            return redirect("forums")


class ConfirmEmailView(View):
    """
    Form confirm email
    """
    template_name = "muss/confirm_email.html"

    def get(self, request, username, activation_key, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect("forums")

        # Decoding username
        username = base64.b64decode(username.encode("utf-8")).decode("ascii")
        # Parameters for template
        data = {'username': username}

        # Check if not expired key
        user_profile = get_object_or_404(
            models.Profile, activation_key=activation_key
        )

        if user_profile.key_expires < timezone.now():
            return render(request, "muss/confirm_email_expired.html", data)

        # Active user
        User = get_user_model()
        user = get_object_or_404(User, username=username)
        user.is_active = True
        user.save()
        return render(request, self.template_name, data)


class NewKeyActivationView(View):
    """
    View for get a new key activation
    """
    template_name = "muss/confirm_email_expired.html"

    def post(self, request, username, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect("forums")

        User = get_user_model()
        user = get_object_or_404(User, username=username)
        email = user.email

        # For confirm email
        data = utils.get_data_confirm_email(email)

        # Update activation key
        profile = get_object_or_404(models.Profile, iduser=user)
        profile.activation_key = data['activation_key']
        profile.key_expires = data['key_expires']
        profile.save()

        # Send email for confirm user
        utils.send_welcome_email(email, username, data['activation_key'])
        data = {'username': username, 'new_key': True}
        return render(request, self.template_name, data)


def reset_password(request):
    """
    This view contains the form
    for reset password of user
    """
    if request.user.is_authenticated():
        return redirect("forums")

    if request.method == "POST":
        messages.success(request, _('Please, check your email'))

    return password_reset(
        request,
        template_name='muss/password_reset_form.html',
        email_template_name='muss/password_reset_email.html',
        subject_template_name='muss/password_reset_subject.txt',
        password_reset_form=PasswordResetForm,
        token_generator=default_token_generator,
        post_reset_redirect='password_reset',
        from_email=None,
        extra_context=None,
        html_email_template_name=None
    )


def reset_pass_confirm(request, uidb64, token):
    """
    This view display form reset confirm pass
    """
    if request.user.is_authenticated():
        return redirect("forums")

    return password_reset_confirm(
        request, uidb64=uidb64, token=token,
        template_name='muss/password_reset_confirm.html',
        token_generator=default_token_generator,
        set_password_form=SetPasswordForm,
        post_reset_redirect=None,
        extra_context=None
    )


def reset_done_pass(request):
    """
    This view display messages
    that successful reset pass
    """
    if request.user.is_authenticated():
        return redirect("forums")

    return password_reset_complete(
        request, extra_context=None,
        template_name='muss/password_reset_complete.html',
    )
