import os
import shutil


def create_folder(path):
    """
    This method create folder.

    Args:
        value (str): Path.
    """
    os.mkdir(path)


def basename(value):
    """
    This method return basename of one path.

    Args:
        value (str): Path.

    Returns:
        string: Basename path.
    """
    return os.path.basename(value)


def exists_folder(route):
    """
    This method verify that exists folder in base to route.

    Args:
        route (str): Path to check if exists.

    Returns:
        bool: Return if exists.
    """
    if os.path.exists(route):
        return True
    else:
        return False


def remove_folder(route_folder):
    """
    This method remove one folder.

    Args:
        route_folder (str): Path folder to remove.
    """
    try:
        shutil.rmtree(route_folder)
    except Exception:
        pass


def remove_file(route_file):
    """
    This method remove one file in base to route and image.

    Args:
        route_file (str): Path file to remove.
    """
    if route_file != "" and route_file is not None:
        if os.path.exists(route_file):
            os.remove(route_file)


def get_route_file(file_path, file_name):
    """
    This method build the path for a file MEDIA.

    Args:
        file_path (str): File path.
        file_name (str): File name.

    Returns:
        str: Concatenate file path + file name.
    """
    try:
        route_file = file_path + "/" + file_name
    except Exception:
        route_file = ""

    return route_file


def get_domain(request):
    """
    Return main domain
    """
    protocol = 'https' if request.is_secure() else 'http'
    host = request.META['HTTP_HOST']
    return protocol + "://" + host


def get_url_topic(request, topic):
    """
    Get url topic
    """
    url = ""
    url += get_domain(request)
    url += "/topic/" + str(topic.pk) + "/" + topic.slug + "/"
    return url
