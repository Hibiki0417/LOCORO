from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden

from .models import Room, RoomStatus, HotelStaff, Hotel, Reservation, ReservationStatus
from .reservation_views import activate_hold_after_cleaning



class RoomStatusView(View):
    """
    店側スタッフが部屋の状態を確認・変更するための画面。
    - GET  : 部屋の情報と現在ステータスを表示
    - POST : ボタン(action)に応じて Room.status を更新
    """

    template_name = "core/manager_room_detail.html"

    def get(self, request, pk):
        """部屋の情報を表示"""
        room = get_object_or_404(Room, pk=pk)
        context = {
            "room": room,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """
        スタッフが押したボタンに応じてステータスを変更する。
        - action = "checkout"   : 利用中 → 清掃中 にする想定
        - action = "clean_done" : 清掃中 → 空室（予約可）にする想定
        必要に応じて分岐を増やせば OK。
        """
        room = get_object_or_404(Room, pk=pk)
        action = request.POST.get("action")

        # 利用終了（チェックアウト）→ 清掃中へ
        if action == "checkout":
            if room.status == RoomStatus.OCCUPIED:
                room.status = RoomStatus.CLEANING
                room.save()

        # 清掃完了 → 空室（予約可）へ
        elif action == "clean_done":
            if room.status == RoomStatus.CLEANING:
                activate_hold_after_cleaning(room)

        # 将来、キープ開始などをここに追加してもいい
        # elif action == "start_hold":
        #     ...

        # 更新後、同じ画面にリダイレクト
        return redirect("core:manager_room_detail", pk=room.pk)


class ManagerRoomDashboardView(LoginRequiredMixin, ListView):
    """
    ホテル全体の空室ステータスを一覧表示するダッシュボード。
    ・フロア別タブ
    ・ステータス別フィルター（オプション）
    """
    model = Room
    template_name = "core/manager_room_dashboard.html"
    context_object_name = "rooms"
    login_url = reverse_lazy("core:manager_login")

    def get_queryset(self):
        qs = Room.objects.select_related("hotel").order_by("floor", "room_number")
        staff = getattr(self.request.user, "staff_profile", None)

        if staff and staff.hotel:
            qs = qs.filter(hotel=staff.hotel)
        else:
            qs = qs.none()

        # フロアでフィルター (?floor=3 など)
        floor = self.request.GET.get("floor")
        if floor:
            try:
                qs = qs.filter(floor=int(floor))
            except ValueError:
                pass

        # ステータスでフィルター (?status=available など)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # フロア一覧（存在するフロアだけ）
        floors = (
            Room.objects.values_list("floor", flat=True)
            .distinct()
            .order_by("floor")
        )

        context["floors"] = floors
        context["current_floor"] = self.request.GET.get("floor")
        context["current_status"] = self.request.GET.get("status")

        # ステータス一覧（ラベル付き）
        context["status_choices"] = [
            (RoomStatus.AVAILABLE, "空室（予約可）"),
            (RoomStatus.HOLDING, "予約中"),
            (RoomStatus.OCCUPIED, "利用中"),
            (RoomStatus.CLEANING, "清掃中"),
            (RoomStatus.UNAVAILABLE, "予約停止中"),
        ]

        return context


class ManagerRoomStatusApiView(LoginRequiredMixin, View):
    """店側ダッシュボードからのステータス更新API"""

    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)

        # ★ ホテルスタッフとホテルの紐付けチェック
        try:
            staff = request.user.staff_profile
        except HotelStaff.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "ホテルスタッフのみ操作できます。"},
                status=403,
            )

        if room.hotel != staff.hotel:
            return JsonResponse(
                {"success": False, "message": "このホテルの部屋ではありません。"},
                status=403,
            )

        action = request.POST.get("action")

        # 退出 → 利用中 → 清掃中 にする
        if action == "checkout":
            if room.status != RoomStatus.OCCUPIED:
                return JsonResponse(
                    {"success": False, "message": "「利用中」の部屋だけ退室できます。"},
                    status=400,
                )
            room.status = RoomStatus.CLEANING

        # 清掃完了 → 清掃中 → 空室（予約可）にする
        elif action == "clean_done":
            if room.status != RoomStatus.CLEANING:
                return JsonResponse(
                    {"success": False, "message": "「清掃中」の部屋だけ清掃完了できます。"},
                    status=400,
                )

            reservation = activate_hold_after_cleaning(room)

            if reservation:
                return JsonResponse(
                    {
                        "success": True,
                        "new_status": room.status,
                        "new_status_label": room.get_status_display(),
                        "message": "様子見予約があったため、30分HOLDに変更しました。",
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "new_status": room.status,
                    "new_status_label": room.get_status_display(),
                    "message": "清掃完了し、空室に変更しました。",
                }
            )
        elif action == "checkin":
                if room.status != RoomStatus.HOLDING:
                    return JsonResponse(
                        {"success": False, "message": "「予約中」の部屋だけ入室済みにできます。"},
                        status=400,
                    )

                reservation = (
                    Reservation.objects
                    .filter(
                        room=room,
                        status=ReservationStatus.HOLDING,
                    )
                    .order_by("-hold_started_at")
                    .first()
                )

                if reservation:
                    reservation.status = ReservationStatus.CHECKED_IN
                    reservation.save(update_fields=["status"])

                room.status = RoomStatus.OCCUPIED

        else:
            return JsonResponse(
                {"success": False, "message": "不正な操作です。"},
                status=400,
            )

        room.save()

        return JsonResponse(
            {
                "success": True,
                "new_status": room.status,
                "new_status_label": room.get_status_display(),
            }
        )


class ManagerHotelSettingsView(LoginRequiredMixin, UpdateView):
    model = Hotel
    template_name = "core/manager_hotel_settings.html"
    fields = ["name", "address", "phone_number", "image", "is_active"]

    def get_object(self, queryset=None):
        staff = getattr(self.request.user, "staff_profile", None)
        if not staff:
            return None
        return staff.hotel

    def dispatch(self, request, *args, **kwargs):
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return HttpResponseForbidden("ホテルスタッフのみ操作できます。")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        staff = getattr(self.request.user, "staff_profile", None)
        hotel = getattr(staff, "hotel", None)

        if hotel:
            context["rooms"] = (
                Room.objects
                .filter(hotel=hotel)
                .order_by("floor", "room_number")
            )
        else:
            context["rooms"] = Room.objects.none()

        return context

    def form_valid(self, form):
        messages.success(self.request, "店舗情報を更新しました。")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:manager_hotel_settings") + "?tab=room-info"
    



class ManagerLoginView(LoginView):
    template_name = "core/manager_login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("core:manager_dashboard")

    def form_valid(self, form):
        user = form.get_user()

        if not hasattr(user, "staff_profile"):
            form.add_error(None, "ホテルスタッフアカウントではありません。")
            return self.form_invalid(form)

        if not user.is_active:
            form.add_error(None, "このアカウントは無効です。")
            return self.form_invalid(form)

        return super().form_valid(form)
    
class ManagerRoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    template_name = "core/manager_room_create.html"
    fields = [
        "room_number",
        "floor",
        "capacity",
        "is_smoking",
        "is_available",
        "base_price",
        "status",
    ]

    def dispatch(self, request, *args, **kwargs):
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return HttpResponseForbidden("ホテルスタッフのみ操作できます。")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        staff = self.request.user.staff_profile
        form.instance.hotel = staff.hotel
        messages.success(self.request, "客室を追加しました。")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:manager_hotel_settings") + "?tab=room-info"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.request.user.staff_profile.hotel
        return context
    
class ManagerRoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = "core/manager_room_confirm_delete.html"
    context_object_name = "room"

    def dispatch(self, request, *args, **kwargs):
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return HttpResponseForbidden("ホテルスタッフのみ操作できます。")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        staff = self.request.user.staff_profile
        return Room.objects.filter(hotel=staff.hotel)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "客室を削除しました。")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("core:manager_hotel_settings") + "?tab=room-info"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.request.user.staff_profile.hotel
        return context

