from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import *


class LyricsInline(admin.StackedInline):
    model = Lyrics
    extra = 0
    max_num = 1
    can_delete = True


class WordInline(admin.TabularInline):
    model = Word
    extra = 1
    fields = (
        "term",
        "translation",
        "phonetic",
        "audio_example",
    )


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = (
        "user",
        "text",
        "is_confirmed",
        "created_at",
    )
    readonly_fields = (
        "created_at",
    )
    autocomplete_fields = (
        "user",
    )


class SongInline(admin.TabularInline):
    model = Song
    extra = 0
    fields = (
        "title",
        "singer",
        "language",
        "year",
        "audio_file",
        "cover",
        "views_count",
    )
    readonly_fields = (
        "views_count",
    )
    autocomplete_fields = (
        "singer",
        "language",
    )
    show_change_link = True


class CollectionSongsInline(admin.TabularInline):
    model = Collection.songs.through
    extra = 1
    autocomplete_fields = (
        "song",
    )
    verbose_name = "Song"
    verbose_name_plural = "Songs"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
    )
    search_fields = (
        "name",
        "code",
    )
    ordering = (
        "name",
    )


@admin.register(Singer)
class SingerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "nationality",
    )
    list_filter = (
        "nationality",
    )
    search_fields = (
        "name",
        "bio",
        "nationality__name",
    )
    autocomplete_fields = (
        "nationality",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
    )
    search_fields = (
        "title",
        "slug",
    )
    prepopulated_fields = {
        "slug": (
            "title",
        )
    }
    ordering = (
        "title",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "title",
    )
    search_fields = (
        "title",
    )
    ordering = (
        "title",
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "singer",
        "album",
        "language",
        "year",
        "views_count",
        "created_at",
    )
    list_filter = (
        "language",
        "singer",
        "album",
        "categories",
        "tags",
        "year",
        "created_at",
    )
    search_fields = (
        "title",
        "singer__name",
        "album__title",
        "language__name",
        "language__code",
    )
    autocomplete_fields = (
        "singer",
        "language",
        "album",
    )
    filter_horizontal = (
        "categories",
        "tags",
    )
    readonly_fields = (
        "duplicate_song_button",
        "created_at",
        "views_count",
        "jalali_date",
    )
    date_hierarchy = "created_at"
    inlines = (
        LyricsInline,
        WordInline,
        CommentInline,
    )

    fieldsets = (
        ("کپی آهنگ", {
            "fields": (
                "duplicate_song_button",
            )
        }),
        ("اطلاعات اصلی", {
            "fields": (
                "title",
                "singer",
                "album",
                "language",
                "year",
            )
        }),
        ("فایل‌ها", {
            "fields": (
                "audio_file",
                "image",
                "cover",
            )
        }),
        ("دسته‌بندی و تگ‌ها", {
            "fields": (
                "categories",
                "tags",
            )
        }),
        ("آمار و تاریخ", {
            "fields": (
                "views_count",
                "created_at",
                "jalali_date",
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:object_id>/duplicate/",
                self.admin_site.admin_view(self.duplicate_song),
                name="musics_song_duplicate",
            ),
        ]

        return custom_urls + urls

    def duplicate_song_button(self, obj):
        if not obj or not obj.pk:
            return "بعد از ذخیره آهنگ، دکمه کپی فعال می‌شود."

        duplicate_url = reverse(
            "admin:musics_song_duplicate",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" href="{}" '
            'style="background:#7c3aed;color:#fff;padding:8px 16px;'
            'border-radius:6px;text-decoration:none;font-weight:700;">'
            'ساخت کپی از این آهنگ'
            '</a>',
            duplicate_url,
        )

    duplicate_song_button.short_description = "کپی آهنگ"

    def duplicate_song(self, request, object_id):
        original_song = get_object_or_404(Song, pk=object_id)

        new_song = Song.objects.create(
            title=f"{original_song.title} - کپی",
            singer=original_song.singer,
            album=original_song.album,
            language=original_song.language,
            year=original_song.year,
            audio_file=original_song.audio_file,
            image=original_song.image,
            cover=original_song.cover,
            views_count=0,
            rating=original_song.rating,
        )

        new_song.categories.set(original_song.categories.all())
        new_song.tags.set(original_song.tags.all())

        try:
            original_lyrics = original_song.lyrics
        except Lyrics.DoesNotExist:
            original_lyrics = None

        if original_lyrics:
            Lyrics.objects.create(
                song=new_song,
                raw_lyrics=original_lyrics.raw_lyrics,
                translated_lyrics=original_lyrics.translated_lyrics,
                synced_lyrics=original_lyrics.synced_lyrics,
            )

        original_words = original_song.important_words.all()

        Word.objects.bulk_create([
            Word(
                song=new_song,
                term=word.term,
                translation=word.translation,
                phonetic=word.phonetic,
                audio_example=word.audio_example,
            )
            for word in original_words
        ])

        messages.success(
            request,
            f"یک کپی از آهنگ «{original_song.title}» ساخته شد.",
        )

        change_url = reverse(
            "admin:musics_song_change",
            args=[new_song.pk],
        )

        return redirect(change_url)



@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "singer",
        "release_date",
    )
    list_filter = (
        "singer",
        "release_date",
    )
    search_fields = (
        "title",
        "singer__name",
    )
    autocomplete_fields = (
        "singer",
    )
    inlines = (
        SongInline,
    )


@admin.register(Lyrics)
class LyricsAdmin(admin.ModelAdmin):
    list_display = (
        "song",
    )
    search_fields = (
        "song__title",
        "raw_lyrics",
        "translated_lyrics",
    )
    autocomplete_fields = (
        "song",
    )


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = (
        "term",
        "translation",
        "song",
        "phonetic",
    )
    list_filter = (
        "song__language",
        "song__singer",
    )
    search_fields = (
        "term",
        "translation",
        "phonetic",
        "song__title",
        "song__singer__name",
    )
    autocomplete_fields = (
        "song",
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_public",
    )
    list_filter = (
        "is_public",
    )
    search_fields = (
        "title",
        "description",
    )
    inlines = (
        CollectionSongsInline,
    )
    exclude = (
        "songs",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "song",
        "is_confirmed",
        "created_at",
    )
    list_filter = (
        "is_confirmed",
        "created_at",
        "song__language",
    )
    search_fields = (
        "user__phone_number",
        "user__full_name",
        "song__title",
        "text",
    )
    autocomplete_fields = (
        "user",
        "song",
    )
    readonly_fields = (
        "created_at",
    )
    actions = (
        "confirm_comments",
        "unconfirm_comments",
    )

    @admin.action(description="تایید کامنت‌های انتخاب‌شده")
    def confirm_comments(self, request, queryset):
        queryset.update(is_confirmed=True)

    @admin.action(description="لغو تایید کامنت‌های انتخاب‌شده")
    def unconfirm_comments(self, request, queryset):
        queryset.update(is_confirmed=False)

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "created_date", "updated_date")
    list_filter = ("created_date", "updated_date")
    search_fields = ("name", "customer__user__full_name")
    filter_horizontal = ("songs",)
    readonly_fields = ("created_date", "updated_date")






