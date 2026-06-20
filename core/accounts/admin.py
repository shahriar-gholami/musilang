from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

from .models import User, Customer, OtpCode


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "full_name",
            "email",
            "is_active",
            "is_customer",
            "is_staff",
            "is_superuser",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError(_("Passwords don't match."))

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this user's password."
        ),
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "full_name",
            "email",
            "otp_token",
            "password",
            "is_active",
            "is_customer",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class CustomerInline(admin.StackedInline):
    model = Customer
    extra = 0
    max_num = 1
    can_delete = False
    fields = (
        "join_date",
        "affiliation_code",
        "has_package",
        "site_pkg_exp_date",
        "has_active_site_package_display",
        "comments_count_display",
    )
    readonly_fields = (
        "join_date",
        "affiliation_code",
        "has_active_site_package_display",
        "comments_count_display",
    )

    @admin.display(description="پکیج فعال دارد؟", boolean=True)
    def has_active_site_package_display(self, obj):
        if not obj.pk:
            return False
        return obj.has_active_site_package()

    @admin.display(description="تعداد کامنت‌ها")
    def comments_count_display(self, obj):
        if not obj.pk:
            return 0
        return obj.get_comments_count()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User

    list_display = (
        "phone_number",
        "full_name",
        "email",
        "is_customer",
        "is_staff",
        "is_active",
        "created_date",
    )
    list_filter = (
        "is_customer",
        "is_staff",
        "is_active",
        "is_superuser",
        "created_date",
    )
    search_fields = (
        "phone_number",
        "full_name",
        "email",
    )
    ordering = ("-created_date",)
    readonly_fields = (
        "created_date",
        "updated_date",
        "last_login",
    )
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    fieldsets = (
        (_("اطلاعات ورود"), {
            "fields": (
                "phone_number",
                "password",
            )
        }),
        (_("اطلاعات شخصی"), {
            "fields": (
                "full_name",
                "email",
                "otp_token",
            )
        }),
        (_("وضعیت حساب"), {
            "fields": (
                "is_active",
                "is_customer",
            )
        }),
        (_("دسترسی‌ها"), {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("تاریخ‌ها"), {
            "fields": (
                "last_login",
                "created_date",
                "updated_date",
            )
        }),
    )

    add_fieldsets = (
        (_("ساخت کاربر جدید"), {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "full_name",
                "email",
                "password1",
                "password2",
                "is_active",
                "is_customer",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
    )

    inlines = (
        CustomerInline,
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "affiliation_code",
        "has_package",
        "active_package_display",
        "site_pkg_exp_date",
        "comments_count_display",
        "join_date",
    )
    list_filter = (
        "has_package",
        "join_date",
        "site_pkg_exp_date",
    )
    search_fields = (
        "user__phone_number",
        "user__full_name",
        "=affiliation_code",
    )
    readonly_fields = (
        "join_date",
        "affiliation_code",
        "active_package_display",
        "comments_count_display",
    )
    autocomplete_fields = (
        "user",
    )
    ordering = (
        "-join_date",
    )

    @admin.display(description="پکیج فعال دارد؟", boolean=True)
    def active_package_display(self, obj):
        return obj.has_active_site_package()

    @admin.display(description="تعداد کامنت‌ها")
    def comments_count_display(self, obj):
        return obj.get_comments_count()


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "code",
        "created",
        "is_expired_display",
    )
    search_fields = (
        "phone_number",
        "=code",
    )
    readonly_fields = (
        "created",
        "is_expired_display",
    )
    ordering = (
        "-created",
    )

    @admin.display(description="منقضی شده؟", boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired()
