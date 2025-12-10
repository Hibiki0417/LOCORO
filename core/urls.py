from django.urls import path
from .views import RoomListView, RoomDetailView, start_hold, RoomStatusView,  ManagerRoomDashboardView
from . import views

app_name = "core" 

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room_list"),
    path("manager/",ManagerRoomDashboardView.as_view(),name="manager_dashboard",),

    path("rooms/<int:pk>/detail", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/start_hold/",start_hold,name="start_hold"),
    path("manager/rooms/<int:pk>/",views.RoomStatusView.as_view(),name="manager_room_detail",),
    path("manager/api/rooms/<int:pk>/status/",views.ManagerRoomStatusApiView.as_view(),name="manager_room_status_api",),


]
