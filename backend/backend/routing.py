from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import daily.routing

application = ProtocolTypeRouter({
    # 'websocket': AuthMiddlewareStack(
    #     URLRouter(
    #         daily.routing.websocket_urlpatterns
    #     )
    # ),
})