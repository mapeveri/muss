from django.shortcuts import get_object_or_404
from muss.models import HitcountTopic, Topic


def create_hitcount_topic(topic_id: str, session: str, ip: str) -> int:
    """
    Create a hitcount topic
    """

    topic = get_object_or_404(Topic, pk=topic_id)
    hit = HitcountTopic.objects.filter(topic=topic)

    # Check if exists hitcount for topic
    if not hit.exists():
        # Create hitcout topic
        HitcountTopic.objects.create(
            topic=topic, data=[{'session': session, 'ip': ip}]
        )
        count = 1
    else:
        # Check if exists the session in the topic
        s = hit.filter(data__contains=[{'session': session, 'ip': ip}])
        if not s.exists():
            # Not exists, then i create the session
            record = hit.first()
            data = record.data
            # Insert new session to existing sessions
            data.append({'session': session, 'ip': ip})
            record.data = data
            # Update record in the field data
            record.save()
            count = len(data)
        else:
            count = len(hit.first().data)

    return count
