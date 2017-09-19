from muss import models
from muss.api.serializers import UserSerializer


def get_categories_forums():
    """
    Get categories forums data
    """
    queryset = []
    categories = models.Category.objects.filter(hidden=False)
    type_api = 'Category'
    id_json_api = 1

    for category in categories:
        queryset.append({
            'type': type_api, 'id': id_json_api,
            'attributes': {
                'name': category.name, 'description': category.description,
                'hidden': category.hidden, 'is-header': True, 'slug': '',
                'parent-id': None, 'topics-count': 0,
                'category-id': None, 'pk': category.pk
            }
        })

        forums = models.Forum.objects.filter(
            category=category, hidden=False, parent=None
        )
        for forum in forums:
            id_json_api = id_json_api + 1
            record = forum.__dict__
            record['category-id'] = record['category_id']
            record['is-header'] = False
            record['parent-id'] = record['parent_id']
            record['topics-count'] = record['topics_count']
            record['pk'] = record['id']

            fields = [
                '_state', 'is_moderate', 'category_id',
                'topics_count', 'id', 'date', 'parent_id'
            ]

            for field in fields:
                del record[field]

            queryset.append({
                'type': type_api, 'id': id_json_api,
                'attributes': record
            })

        id_json_api = id_json_api + 1

    return queryset


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Override payload jwt
    """
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }
