from django.db import models

class Hotel(models.Model):
    """ホテル1軒分を表すモデル"""

    name = models.CharField(max_length=100)             # ホテル名
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    image = models.ImageField(
        upload_to="hotel_images/",
        blank=True,
        null=True,
        verbose_name="ホテル画像"
    )

    is_active = models.BooleanField(default=True)       # 予約受付中かどうか
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ホテル"
        verbose_name_plural = "ホテル一覧"

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
        verbose_name = "部屋"
        verbose_name_plural = "部屋一覧"
        unique_together = ("hotel", "room_number")
        ordering = ["hotel", "room_number"]


    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.room_number}"
    
    def set_status(self, new_status: str):
        """部屋の状態を共通で更新するメソッド"""
        self.status = new_status
        self.save()

class RoomImage(models.Model):
    """部屋ごとの画像（最大20枚想定）"""

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="images",  # room.images でアクセスできるように
        verbose_name="部屋",
    )
    image = models.ImageField(
        upload_to="room_images/",
        verbose_name="画像",
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="メイン画像かどうか",
        help_text="一覧などで優先的に表示したい画像ならチェック",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="アップロード日時",
    )

    class Meta:
        verbose_name = "部屋画像"
        verbose_name_plural = "部屋画像"
        ordering = ["-is_main", "id"]  # メイン画像が先頭に来る

    def __str__(self) -> str:
        return f"{self.room} - image #{self.pk}"


class ReservationStatus(models.TextChoices):
    RESERVED = "reserved", "予約待ち"
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

    hold_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="キープ開始時刻（清掃完了時）",
    )

    hold_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="キープ終了時刻",
    )

    keep_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="延長後の終了時刻",
    )

    extended_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "予約"
        verbose_name_plural = "予約一覧"

    def __str__(self):
        return f"{self.room} - {self.status}"


    # ------------------------------
    # 現在キープ中かどうか判定
    # ------------------------------
    def is_holding(self):
        """キープ状態で、現在時刻がキープ終了前なら True"""
        from django.utils import timezone

        if self.status != ReservationStatus.HOLDING:
            return False

        if self.hold_expires_at and timezone.now() <= self.hold_expires_at:
            return True

        return False

    # ------------------------------
    # キープ期限切れか判定
    # ------------------------------
    def is_hold_expired(self):
        """キープ期限が過ぎているなら True"""
        from django.utils import timezone

        if self.hold_expires_at and timezone.now() > self.hold_expires_at:
            return True

        return False
    
        # 残りキープ時間（分）を返す
    def get_hold_remaining_minutes(self):
        """キープ中なら残り分数を返す。期限切れなら 0、未設定なら None"""
        from django.utils import timezone

        if not self.hold_expires_at:
            return None

        remaining = self.hold_expires_at - timezone.now()
        seconds = remaining.total_seconds()

        if seconds <= 0:
            return 0

        # 小数点以下は切り捨て
        return int(seconds // 60)




class ReservationTicket(models.Model):
    class Status(models.TextChoices):
        HOLD = "HOLD", "1時間予約中"          # チケット有効中（空室待ち）
        KEEPING = "KEEPING", "30分キープ中"  # 清掃完了後、部屋を取り置き中
        EXPIRED = "EXPIRED", "期限切れ"      # 使われなかった or 時間切れ

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="部屋",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.HOLD,
        verbose_name="予約ステータス",
    )
    # チケットを取った時間（いつ1時間カウントが始まったか）
    hold_started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="予約開始時刻",
    )
    # 「この時間までに空室にならなかったら無効」みたいな上限
    hold_expires_at = models.DateTimeField(
        verbose_name="1時間チケットの有効期限",
        null=True,
        blank=True,
    )
    # 清掃完了後の「30分キープ」が切れる時刻
    keep_expires_at = models.DateTimeField(
        verbose_name="30分キープの有効期限",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "予約チケット"
        verbose_name_plural = "予約チケット一覧"

    def __str__(self):
        return f"{self.room} - {self.get_status_display()}"
