from django.urls import path
from core.views import home_view

urlpatterns = [
    path("home/", home_view, name="home"),
    path("home/<uuid:active_chat_uuid>/", home_view, name="home_active_chat"),
]
