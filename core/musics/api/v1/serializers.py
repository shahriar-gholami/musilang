from rest_framework import serializers
from musics.models import *
import re
import unicodedata


def slugify_fa(value):
    value = str(value).strip()

    value = unicodedata.normalize("NFKC", value)
    value = value.replace("ي", "ی").replace("ك", "ک")

    value = re.sub(r"[^\w\s-]", "-", value, flags=re.UNICODE)
    value = re.sub(r"[-\s]+", "-", value, flags=re.UNICODE)

    return value.strip("-").lower()


class SongCreateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    singer = serializers.PrimaryKeyRelatedField(queryset=Singer.objects.all())
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(),
        required=False,
        allow_null=True
    )
    raw_lyrics = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    translated_lyrics = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Song
        fields = [
            "id",
            "title",
            "singer",
            "language",
            "album",
            "year",
            "audio_file",
            "image",
            "cover",
            "raw_lyrics",
            "translated_lyrics",
            "categories",
            "tags",
        ]

    def validate_year(self, value):
        if value is not None and value < 1900:
            raise serializers.ValidationError("سال وارد شده معتبر نیست.")
        return value

    def _get_or_create_categories(self, category_titles):
        categories = []
        for title in category_titles:
            clean_title = title.strip()
            if not clean_title:
                continue
            slug = slugify_fa(clean_title)
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"title": clean_title},
            )
            if category.title != clean_title:
                category.title = clean_title
                category.save(update_fields=["title"])
            categories.append(category)
        return categories

    def _get_or_create_tags(self, tag_titles):
        tags = []
        for title in tag_titles:
            clean_title = title.strip()
            if not clean_title:
                continue
            tag, _ = Tag.objects.get_or_create(title=clean_title)
            tags.append(tag)
        return tags

    def create(self, validated_data):
        category_titles = validated_data.pop("categories", [])
        tag_titles = validated_data.pop("tags", [])
        raw_lyrics = validated_data.pop("raw_lyrics", "")
        translated_lyrics = validated_data.pop("translated_lyrics", "")

        song = Song.objects.create(**validated_data)

        categories = self._get_or_create_categories(category_titles)
        tags = self._get_or_create_tags(tag_titles)

        if categories:
            song.categories.set(categories)
        if tags:
            song.tags.set(tags)

        Lyrics.objects.create(
            song=song,
            raw_lyrics=raw_lyrics or "",
            translated_lyrics=translated_lyrics or "",
        )

        return song
