from muss.models import Forum


def get_childs_forums(forum_obj: Forum) -> list:
    """
    Get forums childs of forum
    """

    forums = []
    for forum in forum_obj.parents.all():
        forums.append({
            'pk': forum.pk, 'slug': forum.slug,
            'name': forum.name
        })

    return forums


def get_parents_forums(forum_obj: Forum) -> list:
    """
    Get forums parent of forum
    """

    forums = []
    if forum_obj:
        if not(forum_obj.parent is None):
            parents = Forum.objects.raw("""
                with recursive forums_parents as (
                    select id, parent_id, name, slug
                        from muss_forum
                        where id = """ + str(forum_obj.pk) + """
                    union all
                    select f.id, f.parent_id, f.name, f.slug
                        from muss_forum f
                        join forums_parents p on p.parent_id = f.id
                    )
                    select * from forums_parents
                    WHERE id <> """ + str(forum_obj.pk) + """
                    ORDER BY id;"""
                                        )

            for forum in parents:
                forums.append({
                    'pk': forum.pk, 'slug': forum.slug,
                    'name': forum.name
                })

    return forums


def get_pending_moderations(forum_obj: Forum) -> bool:
    """
    Check if the forum has topic pending moderations
    """

    if forum_obj.is_moderate:
        total = forum_obj.forums.filter(is_moderate=False).count()
        if total > 0:
            return True

    return False


def get_total_forum_moderate_user(user) -> int:
    """
    Get total of forums that moderate one user.

    Args:
        user (obj): Object user.

    Returns:
        int: Total forum that user moderate.
    """
    return Forum.objects.filter(
        moderators=user
    ).count()
