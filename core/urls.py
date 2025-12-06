from django.urls import path
from .views import RoomListView, RoomDetailView, start_hold
from . import views

app_name = "core" 

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room_list"),
    path("rooms/<int:pk>/detail", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/start_hold/",start_hold,name="start_hold"),

]
