from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import apps
import random
from musics.models import Song, Singer, Collection


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_("The phone number must be set."))

        user = self.model(phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_customer", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=250, default="نام و نام خانوادگی")
    otp_token = models.PositiveIntegerField(null=True, blank=True)
    is_customer = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "حساب کاربری"
        verbose_name_plural = "حساب‌های کاربری"

    def __str__(self):
        return self.phone_number

    @property
    def display_name(self):
        return self.full_name or self.phone_number


class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "کد تایید"
        verbose_name_plural = "کدهای تایید"

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    def is_expired(self, minutes=2):
        expire_time = self.created + timezone.timedelta(minutes=minutes)
        return timezone.now() > expire_time


class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    join_date = models.DateTimeField(auto_now_add=True)
    affiliation_code = models.PositiveIntegerField(unique=True, null=True, blank=True)
    has_package = models.BooleanField(default=False)
    site_pkg_exp_date = models.DateTimeField(null=True, blank=True)
    favorite_songs = models.ManyToManyField(Song, blank=True)
    favorite_artists = models.ManyToManyField(Singer, blank=True)
    favorite_collections = models.ManyToManyField(Collection, blank=True)

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"

    def __str__(self):
        return self.user.phone_number

    def save(self, *args, **kwargs):
        if not self.affiliation_code:
            self.affiliation_code = self.generate_unique_code()

        super().save(*args, **kwargs)

    def generate_unique_code(self):
        code = random.randint(100000, 999999)

        while Customer.objects.filter(affiliation_code=code).exists():
            code = random.randint(100000, 999999)

        return code

    def has_active_site_package(self):
        return bool(
            self.has_package
            and self.site_pkg_exp_date
            and self.site_pkg_exp_date > timezone.now()
        )

    def get_comments_count(self):
        Comment = apps.get_model("musics", "Comment")
        return Comment.objects.filter(user=self.user).count()
