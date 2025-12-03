from django.contrib import admin
from .models import Hotel, Room, Reservation, ReservationTicket

admin.site.register(Hotel)

admin.site.register(Room)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("room", "status", "reserved_at", "hold_expires_at", "extended_minutes")
    list_filter = ("status", "room")

@admin.register(ReservationTicket)
class ReservationTicketAdmin(admin.ModelAdmin):
    list_display = ("room", "status", "hold_started_at", "hold_expires_at", "keep_expires_at")
    list_filter = ("status", "room")
