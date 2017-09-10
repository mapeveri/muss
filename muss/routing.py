from channels import include
from channels.routing import route

from muss import consumers


# Comment topic
comment_topic_ws = [
    route("websocket.connect", consumers.ws_connect_comment_topic),
    route("websocket.disconnect", consumers.ws_disconnect_comment_topic),
]

# Timeline profile user
notification_ws = [
    route("websocket.connect", consumers.ws_connect_notification),
    route("websocket.disconnect", consumers.ws_disconnect_notification),
]

channel_routing = [
    # Comments
    include("muss.routing.comment_topic_ws", path=r"^/ws/comment$"),
    # Notification
    include("muss.routing.notification_ws", path=r"^/ws/notification$"),
]
