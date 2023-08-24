# WebSocket을 위한 설정, TBD

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
#
# from chat.consumers import ChatConsumer
# import chat.routing
#
# application = ProtocolTypeRouter({
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             chat.routing.websocket_urlpatterns, ChatConsumer.as_asgi()
#         )
#     ),
# })