from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime

from .models import Room, Reservation, ReservationStatus, RoomStatus

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
    客側：様子見予約を開始するビュー

    - Reservation を RESERVED で作成
    - keep_expires_at に 1時間後を入れる
    - 清掃完了時に HOLDING へ変更する
    """
    room = get_object_or_404(Room, pk=pk)
    now = timezone.now()

    # すでに有効な様子見予約がある場合は作成しない
    existing_reserved = Reservation.objects.filter(
        room=room,
        status=ReservationStatus.RESERVED,
        keep_expires_at__gt=now,
    ).first()

    if existing_reserved:
        return redirect("core:room_detail", pk=room.pk)

    # すでに有効なHOLDがある場合も作成しない
    existing_holding = Reservation.objects.filter(
        room=room,
        status=ReservationStatus.HOLDING,
        hold_expires_at__gt=now,
    ).first()

    if existing_holding:
        return redirect("core:room_detail", pk=room.pk)

    # 1時間の様子見予約を作成
# 空室の場合は、今すぐ30分HOLDする
    if room.status == RoomStatus.AVAILABLE:
        Reservation.objects.create(
            hotel=room.hotel,
            room=room,
            status=ReservationStatus.HOLDING,
            hold_started_at=now,
            hold_expires_at=now + timezone.timedelta(minutes=30),
        )

        room.status = RoomStatus.HOLDING
        room.save(update_fields=["status", "updated_at"])

        return redirect("core:room_detail", pk=room.pk)

    # 利用中・清掃中の場合は、1時間の様子見予約を作成する
    if room.status in [RoomStatus.OCCUPIED, RoomStatus.CLEANING]:
        Reservation.objects.create(
            hotel=room.hotel,
            room=room,
            status=ReservationStatus.RESERVED,
            keep_expires_at=now + timezone.timedelta(hours=1),
        )

    return redirect("core:room_detail", pk=room.pk)

def activate_hold_after_cleaning(room):
    """
    店側が清掃完了した時に呼ぶ処理。

    有効な様子見予約があれば、30分HOLDへ変更する。
    なければ部屋を空室に戻す。
    """
    now = timezone.now()

    reservation = (
        Reservation.objects
        .filter(
            room=room,
            status=ReservationStatus.RESERVED,
            keep_expires_at__gt=now,
        )
        .order_by("reserved_at")
        .first()
    )

    if reservation:
        reservation.status = ReservationStatus.HOLDING
        reservation.hold_started_at = now
        reservation.hold_expires_at = now + timezone.timedelta(minutes=30)
        reservation.save(update_fields=[
            "status",
            "hold_started_at",
            "hold_expires_at",
        ])

        room.status = RoomStatus.HOLDING
        room.save(update_fields=["status", "updated_at"])
        return reservation

    room.status = RoomStatus.AVAILABLE
    room.save(update_fields=["status", "updated_at"])
    return None

def cleanup_expired_holds():
    """期限切れの様子見(RESERVED)とキープ(HOLDING)をまとめて掃除"""
    now = timezone.now()

    # --- 1) 様子見(1時間) が切れたもの ---
    reserved_expired = Reservation.objects.select_related("room").filter(
        status=ReservationStatus.RESERVED,
        keep_expires_at__lte=now,
    )

    for reservation in reserved_expired:
        room = reservation.room

        reservation.status = ReservationStatus.CANCELLED
        reservation.save(update_fields=["status"])

        # まだ他に有効な予約枠(RESERVED/HOLDING)が無ければ部屋を空室に戻す
        has_active = Reservation.objects.filter(
            room=room,
            status__in=[ReservationStatus.RESERVED, ReservationStatus.HOLDING],
            keep_expires_at__gt=now,
        ).exists()

        if not has_active and room.status == RoomStatus.HOLDING:
            room.status = RoomStatus.AVAILABLE
            room.save(update_fields=["status", "updated_at"])

    # --- 2) 清掃後30分キープ(HOLDING) が切れたもの ---
    holding_expired = Reservation.objects.select_related("room").filter(
        status=ReservationStatus.HOLDING,
        hold_expires_at__lte=now,
    )

    for reservation in holding_expired:
        room = reservation.room

        reservation.status = ReservationStatus.CANCELLED
        reservation.save(update_fields=["status"])

        has_active_hold = Reservation.objects.filter(
            room=room,
            status=ReservationStatus.HOLDING,
            hold_expires_at__gt=now,
        ).exists()

        if not has_active_hold and room.status == RoomStatus.HOLDING:
            room.status = RoomStatus.AVAILABLE
            room.save(update_fields=["status", "updated_at"])
