from django.urls import path
from daily import views

websocket_urlpatterns = [
    path('ws/chat/', views.Test),
]