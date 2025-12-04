from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Room, Reservation
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime

from .models import Room, Reservation, ReservationStatus, RoomStatus

class RoomListView(ListView):
    model = Room
    template_name = 'core/room_list.html'
    context_object_name = 'rooms'


class RoomDetailView(DetailView):
    model = Room
    template_name = 'core/room_detail.html'
    context_object_name = 'room'

@require_POST
def complete_cleaning(request, pk):
    """
    清掃完了ボタンが押されたときに呼ばれるビュー。
    - 対象の部屋を取得
    - その部屋の最新の「予約済み（清掃待ち）」Reservationを1件取得
    - Reservationをキープ状態(HOLDING)に変更
    - 30分後をキープ終了時刻としてセット
    - Roomの状態をholdingに変更
    - 詳細ページにリダイレクト
    """
    room = get_object_or_404(Room, pk=pk)

    # 最新の「予約済み（清掃待ち）」予約を1件だけ取得
    reservation = (
        Reservation.objects
        .filter(room=room, status=ReservationStatus.RESERVED)
        .order_by("-reserved_at")
        .first()
    )

    if reservation:
        now = timezone.now()

        # Reservation側を「キープ中」に更新
        reservation.status = ReservationStatus.HOLDING
        reservation.hold_started_at = now
        reservation.hold_expires_at = now + datetime.timedelta(minutes=30)
        reservation.save()

        # Room側の状態も「予約中(HOLDING)」に更新
        room.set_status(RoomStatus.HOLDING)

    # 処理が終わったら部屋詳細ページに戻す
    return redirect("core:room_detail", pk=room.pk)


@require_POST
def start_hold(request, pk):
    """
    清掃完了 → この部屋を30分キープ開始するビュー

    - Reservation（予約）を1件作成
      - status（予約状態） = HOLDING（キープ中）
      - hold_started_at（キープ開始時刻） = 今
      - hold_expires_at（キープ終了時刻） = 30分後
    - Room.status（部屋状態） = holding（キープ中） に更新
    """

    # 対象の部屋を取得
    room = get_object_or_404(Room, pk=pk)

    # すでにキープ中の予約があるなら、二重作成を防ぐガード
    existing = Reservation.objects.filter(
        room=room,
        status=ReservationStatus.HOLDING,   # status（予約状態）がキープ中
    ).first()
    if existing:
        # もうキープ中なら何もせず詳細ページへ戻る
        return redirect("core:room_detail", pk=room.pk)

    now = timezone.now()                               # now（現在時刻）
    keep_minutes = 30                                  # keep_minutes（キープ時間：30分）
    expires_at = now + datetime.timedelta(minutes=keep_minutes)

    # Reservation（予約）を作成
    reservation = Reservation.objects.create(
        hotel=room.hotel,                              # hotel（どのホテルか）
        room=room,                                     # room（どの部屋か）
        status=ReservationStatus.HOLDING,              # status（予約状態：キープ中）
        hold_started_at=now,                           # hold_started_at（キープ開始）
        hold_expires_at=expires_at,                    # hold_expires_at（キープ終了）
    )

    # Room（部屋）の状態を holding（キープ中）に変更
    room.status = RoomStatus.HOLDING                  # room.status（部屋状態：キープ中）
    room.save(update_fields=["status", "updated_at"])

    return redirect("core:room_detail", pk=room.pk)
