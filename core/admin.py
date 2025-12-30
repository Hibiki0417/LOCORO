from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Hotel,
    Room,
    Reservation,
    ReservationTicket,
    RoomImage,
    HotelStaff,
)

# --------------------
# RoomImage Inline
# --------------------
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 0
    max_num = 20


# --------------------
# Room Admin
# --------------------
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "hotel", "status")
    list_filter = ("hotel", "status")
    inlines = [RoomImageInline]


# --------------------
# Hotel Admin（※ ここだけで Hotel を登録）
# --------------------
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rooms_link")

    def rooms_link(self, obj):
        url = (
            reverse("admin:core_room_changelist")
            + f"?hotel__id__exact={obj.id}"
        )
        return format_html('<a href="{}">部屋一覧を見る</a>', url)

    rooms_link.short_description = "部屋"


# --------------------
# Reservation
# --------------------
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


# --------------------
# ReservationTicket
# --------------------
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


# --------------------
# HotelStaff
# --------------------
@admin.register(HotelStaff)
class HotelStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "hotel", "is_manager")
    list_filter = ("hotel", "is_manager")
