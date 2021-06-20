from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from muss.models import Profile


def get_photo_profile(user: int) -> str:
    """
    This method return photo profile.

    Args:
        user (int): Identification user.

    Returns:
        str: Path photo profile.
    """
    default_photo = static("muss/public/assets/images/profile.png")
    profile = Profile.objects.filter(user=user)
    if profile.count() > 0:
        photo = profile[0].photo
        if photo:
            field_photo = settings.MEDIA_URL + str(photo)
        else:
            field_photo = default_photo
    else:
        field_photo = default_photo

    return field_photo
