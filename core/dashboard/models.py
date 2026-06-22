from django.conf import settings
from django.db import models

class SongRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_REVIEWED = "reviewed"
    STATUS_ADDED = "added"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "در انتظار بررسی"),
        (STATUS_REVIEWED, "بررسی شده"),
        (STATUS_ADDED, "اضافه شده"),
        (STATUS_REJECTED, "رد شده"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="song_requests",
        verbose_name="کاربر"
    )

    singer_name = models.CharField(
        max_length=150,
        verbose_name="نام خواننده"
    )

    song_name = models.CharField(
        max_length=150,
        verbose_name="نام آهنگ"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="وضعیت"
    )

    admin_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت مدیر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "درخواست آهنگ"
        verbose_name_plural = "درخواست‌های آهنگ"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.song_name} - {self.singer_name}"
    
class Ticket(models.Model):
    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.user.full_name} - {self.subject}"


class TicketReply(models.Model):
    main_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply for {self.main_ticket.subject}"

