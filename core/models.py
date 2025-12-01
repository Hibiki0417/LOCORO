from django.db import models

from django.db import models

class Hotel(models.Model):
    """ホテル1軒分を表すモデル"""

    name = models.CharField(max_length=100)             # ホテル名
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)       # 予約受付中かどうか
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
class RoomStatus(models.TextChoices):
    AVAILABLE = "available","空室（予約可）"
    UNAVAILABLE = "unavailable","予約停止中"
    OCCUPIED = "occupied","利用中"
    CLEANING = "cleaning","清掃中"
    HOLDING = "holding","予約中"

class Room(models.Model):
    """各部屋の情報"""

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="rooms",
    )
    room_number = models.CharField(max_length=50)       # 部屋番号 or 名前
    capacity = models.PositiveIntegerField(default=2)   # 何名まで想定か

    is_smoking = models.BooleanField(default=False)     # 喫煙可か
    is_available = models.BooleanField(default=True)    # システム上、予約受付対象か

    base_price = models.DecimalField(                  # 基本料金（税抜き or 税込は後で決める）
        max_digits=8,
        decimal_places=0,
        help_text="通常時の基本料金（円）"
    )
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("hotel", "room_number")     # 同じホテル内で重複禁止
        ordering = ["hotel", "room_number"]

    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.room_number}"

class ReservationStatus(models.TextChoices):
    RESERVED = "reserved", "予約済み（清掃待ち）"
    HOLDING = "holding", "キープ中"
    CHECKED_IN = "checked_in", "利用中"
    COMPLETED = "completed", "利用完了"
    CANCELLED = "cancelled", "キャンセル"

class Reservation(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.RESERVED,
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    extended_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.room} - {self.status}"
