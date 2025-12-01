from django.db import models


from django.db import models


class Hotel(models.Model):
    """ラブホ1軒分を表すモデル"""

    name = models.CharField(max_length=100)             # ホテル名
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)       # 予約受付中かどうか
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("hotel", "room_number")     # 同じホテル内で重複禁止
        ordering = ["hotel", "room_number"]

    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.room_number}"
