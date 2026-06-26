from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import (
    Song,
    Category,
    Tag,
    Language,
    Collection,
    Singer,
    Album,
    Playlist,
)

from blog.models import BlogPost, BlogCategory, BlogTag


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return [
            "musics:index",
            "musics:songs_list",
            "musics:collection_list",
            "musics:artist_list",
            "musics:album_list",
            "musics:playlists",
        ]

    def location(self, item):
        return reverse(item)

class SongSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Song.objects.select_related(
            "singer", "language", "album"
        ).all().order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class TagSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class LanguageSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Language.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class CollectionSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Collection.objects.filter(is_public=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return obj.get_absolute_url()

class SingerSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Singer.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class AlbumSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Album.objects.select_related("singer").all()

    def lastmod(self, obj):
        return obj.release_date

    def location(self, obj):
        return obj.get_absolute_url()

class PlaylistSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Playlist.objects.all().order_by("-updated_date")

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return obj.get_absolute_url()
    
class BlogStaticSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return [
            "blog:post_list",
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(published=True).select_related(
            "category"
        ).prefetch_related(
            "tags"
        ).order_by("-created_date")

    def lastmod(self, obj):
        return obj.created_date

    def location(self, obj):
        return obj.get_absolute_url()


class BlogCategorySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogCategory.objects.all()

    def location(self, obj):
        return reverse("blog:category_post_list", kwargs={
            "category_id": obj.pk,
            "category_slug": obj.get_slug(),
        })


class BlogTagSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogTag.objects.all()

    def location(self, obj):
        return reverse("blog:tag_post_list", kwargs={
            "tag_id": obj.pk,
            "tag_slug": obj.get_slug(),
        })


sitemaps = {
    "static": StaticViewSitemap,
    "songs": SongSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap,
    "languages": LanguageSitemap,
    "collections": CollectionSitemap,
    "artists": SingerSitemap,
    "albums": AlbumSitemap,
    "playlists": PlaylistSitemap,
    "blog_static": BlogStaticSitemap,
    "blog_posts": BlogPostSitemap,
    "blog_categories": BlogCategorySitemap,
    "blog_tags": BlogTagSitemap,
}
