from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from .models import Hotel, Room, Reservation, ReservationStatus
from .reservation_views import cleanup_expired_holds

class CustomerLoginView(LoginView):
    template_name = "core/customer_login.html"

    def form_valid(self, form):
        user = form.get_user()

        if hasattr(user, "staff_profile"):
            messages.error(self.request, "スタッフは管理画面からログインしてください。")
            return redirect("core:manager_login")

        login(self.request, user)
        return redirect("core:hotel_list")


class HotelListView(ListView):
    model = Hotel
    template_name = "core/hotel_list.html"
    context_object_name = "hotels"

    def get_queryset(self):
        # 公開（有効）ホテルだけを一覧表示
        return Hotel.objects.filter(is_active=True).order_by("name")


class RoomListView(ListView):
    model = Room
    template_name = 'core/room_list.html'
    context_object_name = 'rooms'

    def get(self, request, *args, **kwargs):
        # 画面を開くたびに、期限切れのキープを掃除
        cleanup_expired_holds()
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        hotel_id = self.kwargs.get("hotel_id")

        qs = (
            Room.objects
            .select_related("hotel")
            .prefetch_related("images")
        )

        if hotel_id:
            qs = qs.filter(hotel_id=hotel_id)

        return qs


class RoomDetailView(DetailView):
    model = Room
    template_name = 'core/room_detail.html'
    context_object_name = 'room'

    def get(self, request, *args, **kwargs):
        # 詳細画面を開くたびにも掃除しておく
        cleanup_expired_holds()
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return (
            Room.objects
            .select_related("hotel")
            .prefetch_related("images")
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        now = timezone.now()

        # この部屋の「現在キープ中」の予約を1件だけ取得
        active_reservation = (
            Reservation.objects
            .filter(
                room=room,
                status=ReservationStatus.HOLDING,
                hold_expires_at__gt=now,  # まだ期限前
            )
            .order_by("-hold_expires_at")
            .first()
        )

        context["active_reservation"] = active_reservation
        return context