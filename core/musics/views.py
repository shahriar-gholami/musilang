from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q
from .models import *
from django.core.paginator import Paginator
from orders.models import Package
from django.contrib import messages
from django.db.models import Count, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg




class IndexPageView(View):
    def get(self, request):
        songs = Song.objects.select_related("singer", "language", "album", "lyrics").all()
        collections = (
        Collection.objects
        .filter(is_public=True)
        .annotate(songs_count=Count("songs", distinct=True))
        .prefetch_related(
            Prefetch(
                "songs",
                queryset=Song.objects.select_related("singer").only(
                    "id",
                    "title",
                    "singer__id",
                    "singer__name",
                )
            )
        )
        .order_by("-id")[:8]
        )
        context = {

            'songs': songs,
            'collections': collections,
            'singers': Singer.objects.all().order_by("name"),
            'latest_songs': Song.objects.order_by('-created_at')[:10],
            'top_rated_songs': Song.objects.order_by('-rating')[:10],
            'special_tags': Tag.objects.filter(is_special=True),
            'categories': Category.objects.all(),
            # 'latest_posts': BlogPost.objects.filter(is_published=True)[:4] if BlogPost.objects.exists() else [],
            'packages': Package.objects.filter(is_active=True)[:3] if Package.objects.exists() else [],
        }
        return render(request, 'musics/index.html', context)


class BaseSongListView(View):
    """کلاس پایه برای مدیریت مرتب‌سازی در لیست‌های آهنگ"""

    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "rating_desc": "-rating",
        "rating_asc": "rating",
    }

    def get_queryset(self, queryset):
        sort = self.request.GET.get("sort", "newest")
        ordering = self.sort_options.get(sort, "-created_at")
        return queryset.order_by(ordering)


class SongListView(BaseSongListView):
    template_name = "musics/song_list.html"
    paginate_by = 24

    def get(self, request, *args, **kwargs):
        queryset = (
            Song.objects
            .select_related("singer", "lyrics")
            .prefetch_related("categories", "tags")
        )

        queryset = self.get_queryset(queryset)

        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": request.GET.get("sort", "newest"),
        }

        return render(request, self.template_name, context)


class SongsListByCategoryView(BaseSongListView):
    template_name = "musics/category_songs.html"
    paginate_by = 24

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)

        queryset = (
            Song.objects
            .filter(categories=category)
            .select_related("singer", "lyrics")
            .prefetch_related("categories", "tags")
        )

        queryset = self.get_queryset(queryset)

        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "category": category,
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": request.GET.get("sort", "newest"),
        }

        return render(request, self.template_name, context)


class SongsListByTagView(BaseSongListView):
    template_name = "musics/tag_songs.html"
    paginate_by = 24

    def get(self, request, tag_id, tag_slug=None):
        tag = get_object_or_404(Tag, id=tag_id)

        queryset = (
            Song.objects
            .filter(tags=tag)
            .select_related("singer", "language", "album")
            .prefetch_related("categories", "tags")
            .distinct()
        )

        queryset = self.get_queryset(queryset)

        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "tag": tag,
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": request.GET.get("sort", "newest"),
        }

        return render(request, self.template_name, context)


class SongsListByLanguage(BaseSongListView):
    template_name = "musics/language_songs.html"
    paginate_by = 24

    def get(self, request, code):
        language = get_object_or_404(Language, code=code)

        queryset = (
            Song.objects
            .filter(language=language)
            .select_related("singer", "language", "album")
            .prefetch_related("categories", "tags")
            .distinct()
        )

        queryset = self.get_queryset(queryset)

        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "language": language,
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": request.GET.get("sort", "newest"),
        }

        return render(request, self.template_name, context)


class SearchView(View):
    paginate_by = 12

    def get(self, request):
        query = request.GET.get("q", "").strip()
        current_sort = request.GET.get("sort", "newest")

        songs = Song.objects.none()

        if query:
            songs = Song.objects.select_related(
                "singer",
                "language",
                "album",
            ).prefetch_related(
                "categories",
                "tags",
            ).filter(
                Q(title__icontains=query) |
                Q(singer__name__icontains=query) |
                Q(album__title__icontains=query) |
                Q(categories__title__icontains=query) |
                Q(tags__title__icontains=query) |
                Q(language__name__icontains=query)
            ).distinct()

            if current_sort == "oldest":
                songs = songs.order_by("created_at")
            elif current_sort == "rating_desc":
                songs = songs.order_by("-rating", "-created_at")
            elif current_sort == "rating_asc":
                songs = songs.order_by("rating", "-created_at")
            else:
                songs = songs.order_by("-created_at")

        paginator = Paginator(songs, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "query": query,
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": current_sort,
            "special_tags": Tag.objects.filter(is_special=True),
            "categories": Category.objects.all(),
            "languages": Language.objects.all(),
            "singers": Singer.objects.all(),
        }

        return render(request, "musics/search_results.html", context)


from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Song, Singer, Tag, Category, Language, Comment


class SingleSongDetailView(View):
    def get(self, request, pk, song_slug):
        confirmed_comments = Comment.objects.select_related("user").filter(
            is_confirmed=True
        ).order_by("-created_at")

        song = get_object_or_404(
            Song.objects.select_related(
                "singer",
                "language",
                "album",
            ).prefetch_related(
                "categories",
                "tags",
                Prefetch("comments", queryset=confirmed_comments),
            ),
            pk=pk,
        )

        song.views_count += 1
        song.save(update_fields=["views_count"])

        song_category_ids = song.categories.values_list("id", flat=True)
        song_tag_ids = song.tags.values_list("id", flat=True)

        related_songs = Song.objects.select_related(
            "singer",
            "language",
            "album",
        ).prefetch_related(
            "categories",
            "tags",
        ).filter(
            language=song.language,
        ).exclude(
            id=song.id,
        ).annotate(
            common_categories_count=Count(
                "categories",
                filter=Q(categories__id__in=song_category_ids),
                distinct=True,
            ),
            common_tags_count=Count(
                "tags",
                filter=Q(tags__id__in=song_tag_ids),
                distinct=True,
            ),
        ).filter(
            Q(common_categories_count__gt=0) |
            Q(common_tags_count__gt=0)
        ).order_by(
            "-common_categories_count",
            "-common_tags_count",
            "-rating",
            "-created_at",
        )[:10]

        context = {
            "song": song,
            "lyrics": getattr(song, "lyrics", None),
            "comments": song.comments.all(),
            "all_singers": Singer.objects.all(),
            "special_tags": Tag.objects.filter(is_special=True),
            "categories": Category.objects.all(),
            "languages": Language.objects.all(),
            "related_songs": related_songs,
        }

        return render(request, "musics/song_detail.html", context)
    

class CreateSongCommentView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, pk):
        song = get_object_or_404(Song, pk=pk)
        text = request.POST.get("text", "").strip()

        if not text:
            messages.error(request, "متن دیدگاه نمی‌تواند خالی باشد.")
            return redirect(song.get_absolute_url())

        Comment.objects.create(
            user=request.user,
            song=song,
            text=text,
            is_confirmed=False,
        )

        messages.success(
            request,
            "دیدگاه شما ثبت شد و پس از تایید نمایش داده می‌شود."
        )
        return redirect(song.get_absolute_url())


class CreateSongRatingView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, pk):
        song = get_object_or_404(Song, pk=pk)
        score = request.POST.get("score")

        try:
            score = int(score)
        except (TypeError, ValueError):
            messages.error(request, "لطفاً یک امتیاز معتبر انتخاب کنید.")
            return redirect(song.get_absolute_url())

        if score < 1 or score > 5:
            messages.error(request, "امتیاز باید بین ۱ تا ۵ باشد.")
            return redirect(song.get_absolute_url())

        SongRating.objects.update_or_create(
            user=request.user,
            song=song,
            defaults={"score": score},
        )

        average_rating = SongRating.objects.filter(song=song).aggregate(
            average=Avg("score")
        )["average"]

        if average_rating is not None:
            song.rating = round(average_rating, 1)
            song.save(update_fields=["rating"])

        messages.success(request, "امتیاز شما با موفقیت ثبت شد.")
        return redirect(song.get_absolute_url())


class CollectionListView(View):
    template_name = "musics/collection_list.html"
    paginate_by = 12

    def get_queryset(self):
        sort = self.request.GET.get("sort", "newest")

        songs_queryset = (
            Song.objects
            .select_related("singer", "language", "album")
            .prefetch_related("categories", "tags")
            .order_by("-created_at")
        )

        queryset = (
            Collection.objects
            .filter(is_public=True)
            .annotate(
                songs_count=Count("songs", distinct=True)
            )
            .prefetch_related(
                Prefetch("songs", queryset=songs_queryset)
            )
        )

        if sort == "oldest":
            queryset = queryset.order_by("created_at")
        elif sort == "songs_desc":
            queryset = queryset.order_by("-songs_count", "-created_at")
        elif sort == "songs_asc":
            queryset = queryset.order_by("songs_count", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")


        return queryset

    def get(self, request):
        collections_queryset = self.get_queryset()

        paginator = Paginator(collections_queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "collections": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": request.GET.get("sort", "newest"),
        }

        return render(request, self.template_name, context)


from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Collection, Song


from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from .models import Collection, Song


from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Collection, Song


class CollectionDetailView(View):
    template_name = "musics/collection_detail.html"

    def get(self, request, pk, collection_slug):
        songs_queryset = (
            Song.objects
            .select_related("singer", "language", "album")
            .prefetch_related("categories", "tags")
            .order_by("id")
        )

        collection = get_object_or_404(
            Collection.objects.filter(pk=pk, is_public=True)
            .prefetch_related(
                Prefetch("songs", queryset=songs_queryset)
            )
        )

        if collection.get_collection_slug() != collection_slug:
            return redirect(collection.get_absolute_url())

        songs = list(collection.songs.all())

        return render(request, self.template_name, {
            "collection": collection,
            "songs": songs,
        })


class ArtistListView(View):
    template_name = "musics/artist_list.html"
    paginate_by = 12

    def get(self, request):
        artists_qs = (
            Singer.objects
            .select_related("nationality")
            .order_by("name")
        )

        paginator = Paginator(artists_qs, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "artists": page_obj.object_list
        })


class ArtistDetailView(View):
    template_name = "musics/artist_detail.html"

    def get(self, request, pk, artist_slug):
        artist = get_object_or_404(
            Singer.objects.select_related("nationality"),
            pk=pk
        )

        if artist.get_artist_slug() != artist_slug:
            return redirect(artist.get_absolute_url())

        songs = (
            Song.objects
            .filter(singer=artist)
            .select_related("album", "language", "lyrics", "singer")
            .prefetch_related("categories", "tags")
            .order_by("-created_at")
        )

        albums = (
            Album.objects
            .filter(singer=artist)
            .select_related("singer")
            .order_by("-release_date", "-id")
        )

        return render(request, self.template_name, {
            "artist": artist,
            "songs": songs,
            "albums": albums,
        })


class AlbumListView(View):
    template_name = "musics/album_list.html"
    paginate_by = 12

    def get(self, request):
        albums_qs = (
            Album.objects
            .select_related("singer", "singer__nationality")
            .annotate(songs_count=Count("songs"))
            .order_by("-release_date", "-id")
        )

        paginator = Paginator(albums_qs, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            "albums": page_obj.object_list,
            "page_obj": page_obj,
        })


class AlbumDetailView(View):
    template_name = "musics/album_detail.html"

    def get(self, request, pk, album_slug):
        album = get_object_or_404(
            Album.objects
            .select_related("singer", "singer__nationality")
            .annotate(songs_count=Count("songs")),
            pk=pk
        )

        if album.get_album_slug() != album_slug:
            return redirect(album.get_absolute_url())

        songs = (
            Song.objects
            .filter(album=album)
            .select_related("singer", "language", "album", "lyrics")
            .prefetch_related("categories", "tags")
            .order_by("-created_at")
        )

        return render(request, self.template_name, {
            "album": album,
            "songs": songs,
            "songs_count": album.songs_count,
        })
