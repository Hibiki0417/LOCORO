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

    def get(self, request, *args, **kwargs):
        # 画面を開くたびに、期限切れのキープを掃除
        cleanup_expired_holds()
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        # Roomに紐づく画像も一緒に取得
        return (
            Room.objects
            .select_related("hotel")
            .prefetch_related("images")  # related_name="images"
        )


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
        - status（予約状態）  → HOLDING（キープ中）
        - hold_started_at（キー予約開始刻）→ 今
        - hold_expires_at（キー終了刻）    → 30分後
    - Room.status（部屋の状態）を holding（キープ中）に更新
    """

    # 対象の部屋を取得
    room = get_object_or_404(Room, pk=pk)

    # 現在時刻
    now = timezone.now()

    # すでに「有効なキープ中」の予約があるか確認（ダブり防止）
    existing = (
        Reservation.objects
        .filter(
            room=room,
            status=ReservationStatus.HOLDING,   # キープ中
            hold_expires_at__gt=now,            # まだ期限前のものだけ
        )
        .first()
    )

    if existing:
        # すでにキープ中なら何もせず詳細ページへ戻る
        return redirect("core:room_detail", pk=room.pk)

    # ここから新しい Reservation を作成
    keep_minutes = 30
    expires_at = now + timezone.timedelta(minutes=keep_minutes)

    reservation = Reservation.objects.create(
        hotel=room.hotel,
        room=room,
        status=ReservationStatus.HOLDING,
        hold_started_at=now,
        hold_expires_at=expires_at,
    )

    # Room（部屋）の状態も holding（キープ中）に変更
    room.status = ReservationStatus.HOLDING
    room.save(update_fields=["status", "updated_at"])

    return redirect("core:room_detail", pk=room.pk)


def cleanup_expired_holds():
    """
    期限切れのキープ(HOLDING)を掃除する（画面を開いたときに実行）

    - hold_expires_at <= 現在 の Reservation(HOLDING) を CANCELLED にする
    - 対象の Room に「まだ有効なキープ」がなければ、Room.status を AVAILABLE に戻す
    """
    now = timezone.now()

    # 期限切れになっている「キープ中」の予約を全部取得
    expired_qs = (
        Reservation.objects
        .select_related("room")
        .filter(
            status=ReservationStatus.HOLDING,
            hold_expires_at__lte=now,
        )
    )

    for reservation in expired_qs:
        room = reservation.room

        # この予約を「期限切れ扱い」に変更
        reservation.status = ReservationStatus.CANCELLED
        reservation.save(update_fields=["status"])

        # この部屋に、まだ有効なキープが他に残っているか？
        has_active_hold = Reservation.objects.filter(
            room=room,
            status=ReservationStatus.HOLDING,
            hold_expires_at__gt=now,      # まだ期限前
        ).exists()

        # 他に有効なキープがなければ、部屋を空室に戻す
        if not has_active_hold and room.status == RoomStatus.HOLDING:
            room.status = RoomStatus.AVAILABLE
            room.save(update_fields=["status", "updated_at"])