import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _

from muss import notifications_email as nt_email
from muss.models import Profile


def confirm_email(username: str, csrf_token: str,
                  activation_key: str, template_name: str) -> str:
    """
    Confirm email user
    """

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
        Profile, activation_key=activation_key.strip()
    )

    if user_profile.key_expires < timezone.now():
        template = render_to_string(
            "muss/confirm_email_expired.html", data)
        return template

    # Active user
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    user.is_active = True
    user.save()
    template = render_to_string(template_name, data)

    return template


def new_key_activation(username: str) -> None:
    """
    Generate new activation key
    """

    User = get_user_model()
    user = get_object_or_404(User, username=username)
    email = user.email

    # For confirm email
    data = nt_email.get_data_confirm_email(email)

    # Update activation key
    profile = get_object_or_404(Profile, user=user)
    profile.activation_key = data['activation_key']
    profile.key_expires = data['key_expires']
    profile.save()

    # Send email for confirm user
    nt_email.send_welcome_email(
        email, username, data['activation_key']
    )


def reset_password(email: str, http_host: str, is_secure: bool) -> None:
    """
    Email reset password
    """

    User = get_user_model()
    user = get_object_or_404(User, email=email)

    subject_template_name = "muss/password_reset_subject.txt"
    email_template_name = "muss/password_reset_email.html"
    context = context = {
        'email': email,
        'domain': http_host,
        'site_name': settings.SITE_NAME,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if is_secure else 'http',
    }
    from_email = None
    to_email = email

    nt_email.send_mail_reset_password(
        subject_template_name, email_template_name, context,
        from_email, to_email
    )


def reset_password_confirm(uidb64: str, token: str,
                           password: str, valid_link: bool) -> dict:
    """
    Confirm reset password
    """

    User = get_user_model()
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    message = ""
    status = 200
    token_generator = default_token_generator
    if user is not None and token_generator.check_token(user, token):
        # Is a valid link
        if valid_link:
            return {"status": status, "message": message}

        if password:
            # Update password user
            user.set_password(password)
            user.save()
        else:
            # Invalid form
            message = str(_("Failed to reset password."))
    else:
        # Invalid link
        message = _(
            "The password reset link was invalid, "
            "possibly because it has already been used. "
            "Please request a new password reset."
        )
        status = 404

    return {"status": status, "message": message}
