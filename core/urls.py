from django.urls import path
from .views import RoomListView, RoomDetailView, complete_cleaning
from . import views


urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room_list"),
    path("rooms/<int:pk>/detail", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/complete_cleaning/",complete_cleaning,name="complete_cleaning"),

]
