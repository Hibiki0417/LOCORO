from django.contrib import admin
from .models import Hotel, Room, Reservation, ReservationTicket

# Hotel 管理
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "is_active")
    list_filter = ("is_active",)

# Room 管理
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hotel", "room_number", "status", "is_available")
    list_filter = ("status", "hotel")

# Reservation 管理（予約）
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "hotel",
        "room",
        "status",
        "reserved_at",
        "hold_started_at",
        "hold_expires_at",
        "extended_minutes",
    )
    list_filter = ("status", "hotel", "room")

# ReservationTicket 管理（ユーザーの予約権利）
@admin.register(ReservationTicket)
class ReservationTicketAdmin(admin.ModelAdmin):
    list_display = (
        "room",
        "status",
        "hold_started_at",
        "hold_expires_at",
        "keep_expires_at",
    )
    list_filter = ("status", "room")
