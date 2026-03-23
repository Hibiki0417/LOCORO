from django.urls import path
from .views import RoomListView, RoomDetailView, start_hold, RoomStatusView,  ManagerRoomDashboardView, ManagerHotelSettingsView, HotelListView
from . import views
from django.contrib.auth import views as auth_views

app_name = "core" 

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room_list"),
    path("hotels/", HotelListView.as_view(), name="hotel_list"),

    path("manager/login/", views.ManagerLoginView.as_view(), name="manager_login"),
    path("manager/",ManagerRoomDashboardView.as_view(),name="manager_dashboard",),
    path("manager/hotel/settings/", views.ManagerHotelSettingsView.as_view(), name="manager_hotel_settings"),
    path("manager/logout/", auth_views.LogoutView.as_view(), name="manager_logout"),

    path("rooms/<int:pk>/detail", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/start_hold/",start_hold,name="start_hold"),
    path("manager/rooms/<int:pk>/",views.RoomStatusView.as_view(),name="manager_room_detail",),
    path("manager/api/rooms/<int:pk>/status/",views.ManagerRoomStatusApiView.as_view(),name="manager_room_status_api",),
    path("hotels/<int:hotel_id>/rooms/",views.RoomListView.as_view(),name="hotel_room_list",),

    

]
