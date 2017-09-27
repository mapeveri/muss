from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from .models import Forum, Topic


class TopicFeed(Feed):
    """
    Topic feed for rss and atom.

    - **parameters**:
        :param title: Tittle feed.
        :param description: Description feed.
    """
    # attr basic of feed
    title = 'Forum rss'
    description = 'Feed for forums'

    def get_object(self, request, *args, **kwargs):
        forum = get_object_or_404(
            Forum, pk=kwargs['pk'], slug=kwargs['forum']
        )
        return forum

    def items(self, forum):
        # Get forum
        return Topic.objects.filter(forum=forum)

    def item_link(self, item):
        print(item)
        pk = str(item.pk)
        slug = item.slug
        # For url topic frontend
        return settings.SITE_URL + "/topic/" + pk + "/" + slug + "/"

    def link(self, forum):
        return reverse('rss', args=[
            forum.pk, forum.slug
        ])

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.date
