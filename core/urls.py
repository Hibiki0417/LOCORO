from django.urls import path
from django.contrib.auth import views as auth_views

from .customer_views import (
    HotelListView,
    RoomListView,
    RoomDetailView,
    CustomerLoginView,
)

from .reservation_views import start_hold

from .views2 import (
    RoomStatusView,
    ManagerRoomDashboardView,
    ManagerHotelSettingsView,
    ManagerLoginView,
    ManagerRoomCreateView,
    ManagerRoomDeleteView,
    ManagerRoomStatusApiView,
)
app_name = "core" 

urlpatterns = [
    # 公開ページ
    path("hotels/", HotelListView.as_view(), name="hotel_list"),
    path("hotels/<int:hotel_id>/rooms/", RoomListView.as_view(), name="hotel_room_list"),
    path("rooms/<int:pk>/detail/", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/start_hold/", start_hold, name="start_hold"),

    # 客側認証
    path("login/", CustomerLoginView.as_view(), name="customer_login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="core:hotel_list"), name="customer_logout"),

    # 店側認証
    path("manager/login/", ManagerLoginView.as_view(), name="manager_login"),
    path("manager/logout/", auth_views.LogoutView.as_view(next_page="core:manager_login"), name="manager_logout"),

    # 店側画面
    path("manager/", ManagerRoomDashboardView.as_view(), name="manager_dashboard"),
    path("manager/hotel/settings/", ManagerHotelSettingsView.as_view(), name="manager_hotel_settings"),
    path("manager/rooms/create/", ManagerRoomCreateView.as_view(), name="manager_room_create"),
    path("manager/rooms/<int:pk>/", RoomStatusView.as_view(), name="manager_room_detail"),
    path("manager/rooms/<int:pk>/delete/", ManagerRoomDeleteView.as_view(), name="manager_room_delete"),

    # API
    path("manager/api/rooms/<int:pk>/status/", ManagerRoomStatusApiView.as_view(), name="manager_room_status_api"),
]
