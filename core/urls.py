from django.urls import path
from .views import RoomListView, RoomDetailView, start_hold, RoomStatusView,  ManagerRoomDashboardView, ManagerHotelSettingsView, HotelListView,  ManagerRoomCreateView, ManagerRoomDeleteView
from . import views
from django.contrib.auth import views as auth_views

app_name = "core" 

urlpatterns = [
    # 公開ページ
    path("hotels/", HotelListView.as_view(), name="hotel_list"),
    path("hotels/<int:hotel_id>/rooms/", views.RoomListView.as_view(), name="hotel_room_list"),
    path("rooms/<int:pk>/detail/", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/start_hold/", start_hold, name="start_hold"),

    # 客側認証
    path("login/", views.CustomerLoginView.as_view(), name="customer_login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="core:hotel_list"), name="customer_logout"),

    # 店側認証
    path("manager/login/", views.ManagerLoginView.as_view(), name="manager_login"),
    path("manager/logout/", auth_views.LogoutView.as_view(next_page="core:manager_login"), name="manager_logout"),

    # 店側画面
    path("manager/", ManagerRoomDashboardView.as_view(), name="manager_dashboard"),
    path("manager/hotel/settings/", views.ManagerHotelSettingsView.as_view(), name="manager_hotel_settings"),
    path("manager/rooms/create/", views.ManagerRoomCreateView.as_view(), name="manager_room_create"),
    path("manager/rooms/<int:pk>/", views.RoomStatusView.as_view(), name="manager_room_detail"),
    path("manager/rooms/<int:pk>/delete/", views.ManagerRoomDeleteView.as_view(), name="manager_room_delete"),

    # API
    path("manager/api/rooms/<int:pk>/status/", views.ManagerRoomStatusApiView.as_view(), name="manager_room_status_api"),
]
