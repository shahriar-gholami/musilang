from django.contrib import admin

from .models import SongRequest


@admin.register(SongRequest)
class SongRequestAdmin(admin.ModelAdmin):
    list_display = (
        "song_name",
        "singer_name",
        "user",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "song_name",
        "singer_name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )


    from django.contrib import admin

from .models import Ticket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    fields = ("body", "created_date")
    readonly_fields = ("created_date",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "subject",
        "is_answered",
        "is_closed",
        "created_date",
    )
    list_filter = (
        "is_answered",
        "is_closed",
        "created_date",
    )
    search_fields = (
        "subject",
        "body",
        "customer__user__full_name",
    )
    readonly_fields = ("created_date",)
    inlines = (TicketReplyInline,)



