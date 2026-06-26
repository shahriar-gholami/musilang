from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from khayyam import JalaliDatetime
import os
import uuid

def upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    folder = instance.__class__.__name__.lower()
    return f"music/{folder}/{uuid.uuid4().hex}{ext}"

class Language(models.Model):
    name = models.CharField(max_length=50,verbose_name=_("Language Name"))
    code = models.CharField(max_length=10,unique=True,verbose_name=_("ISO Code (e.g. en, fr)"))

    def get_absolute_url(self):
        return reverse("musics:songs_by_language", kwargs={
            "code": self.code
        })

    def __str__(self):
        return self.name

class Singer(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    is_special = models.BooleanField(default=False)
    nationality = models.ForeignKey(Language,on_delete=models.SET_NULL,null=True)

    def get_artist_slug(self):
        return self.name.replace(" ", "-")

    def get_absolute_url(self):
        return reverse("musics:artist_detail", kwargs={
            "pk": self.pk,
            "artist_slug": self.get_artist_slug()
        })

    def __str__(self):
        return self.name

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def get_absolute_url(self):
        return reverse("musics:songs_by_category", kwargs={
            "slug": self.slug
        })

    def __str__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField(max_length=100)
    is_special = models.BooleanField(default=False)

    def get_slug(self):
        return self.title.replace(" ", "-")
    
    def get_latest_songs(self):
        return self.songs.all().order_by('-created_at')[:4]


    def get_absolute_url(self):
        return reverse("musics:songs_by_tag", kwargs={
            "tag_id": self.pk,
            "tag_slug": self.get_slug()
        })

    def __str__(self):
        return self.title

class Song(models.Model):
    title = models.CharField(max_length=255)
    singer = models.ForeignKey(Singer,on_delete=models.CASCADE,related_name="songs")
    language = models.ForeignKey(Language,on_delete=models.PROTECT)
    album = models.ForeignKey("Album",on_delete=models.SET_NULL,null=True,blank=True,related_name="songs")
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    audio_file = models.FileField(upload_to=upload_to)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    cover = models.ImageField(upload_to=upload_to, blank=True, null=True)
    categories = models.ManyToManyField(Category,blank=True,related_name="songs")
    tags = models.ManyToManyField(Tag,blank=True,related_name="songs")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=4.5)

    def get_song_slug(self):
        return self.title.replace(" ", "-")

    def get_absolute_url(self):
        return reverse("musics:song_detail", kwargs={
            "pk": self.pk,
            "song_slug": self.get_song_slug()
        })

    @property
    def has_lyrics(self):
        return hasattr(self, "lyrics")


    @property
    def jalali_date(self):
        if self.created_at:
            return JalaliDatetime(self.created_at).strftime("%Y/%m/%d")
        return "ثبت نشده" # یا می توانید "" (رشته خالی) برگردانید

    def __str__(self):
        return self.title

class Album(models.Model):
    title = models.CharField(max_length=255)
    singer = models.ForeignKey(Singer,on_delete=models.CASCADE,related_name="albums")
    cover = models.ImageField(upload_to=upload_to, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    def get_album_slug(self):
        return self.title.replace(" ", "-")

    def get_absolute_url(self):
        return reverse("musics:album_detail", kwargs={
            "pk": self.pk,
            "album_slug": self.get_album_slug()
        })

    def __str__(self):
        return f"{self.title} - {self.singer.name}"

class Lyrics(models.Model):
    song = models.OneToOneField(Song,on_delete=models.CASCADE,related_name="lyrics")
    raw_lyrics = models.TextField()
    translated_lyrics = models.TextField()
    # برای پخش همزمان:
    # [
    #   {
    #       "start_time": "00:12",
    #       "text": "Hello",
    #       "translation": "سلام"
    #   }
    # ]
    synced_lyrics = models.JSONField(
        help_text=_("JSON structure containing timestamps, text and translation"),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Lyrics for {self.song.title}"


class Word(models.Model):
    song = models.ForeignKey(Song,on_delete=models.CASCADE,related_name="important_words")
    term = models.CharField(max_length=100,verbose_name=_("Word/Phrase"))
    translation = models.CharField(max_length=255)
    phonetic = models.CharField(max_length=100, blank=True, null=True)
    audio_example = models.FileField(upload_to="words/audio/",blank=True,null=True)

    def __str__(self):
        return f"{self.term} ({self.song.title})"


class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    songs = models.ManyToManyField(Song,related_name="collections")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def get_collection_slug(self):
        return self.title.replace(" ", "-")

    def get_absolute_url(self):
        return reverse("musics:collection_detail", kwargs={
            "pk": self.pk,
            "collection_slug": self.get_collection_slug()
        })

    @property
    def preview_singers(self):
        singers = []
        singer_ids = set()

        for song in self.songs.all():
            if song.singer_id and song.singer_id not in singer_ids:
                singers.append(song.singer)
                singer_ids.add(song.singer_id)

            if len(singers) >= 3:
                break

        return singers

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE)
    song = models.ForeignKey(Song,on_delete=models.CASCADE,related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} on {self.song.title}"

class SongRating(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name="song_ratings")
    song = models.ForeignKey(Song,on_delete=models.CASCADE,related_name="ratings")
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_song_rating"
            )
        ]

    def __str__(self):
        return f"{self.user} rated {self.song.title}: {self.score}"


class Playlist(models.Model):
    title = models.CharField(max_length=255)
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_collection_slug(self):
        return self.title.replace(' ','-').replace('/','-')
    
    def get_absolute_url(self):
        return reverse("musics:playlist_detail", kwargs={
            "pk": self.pk,
            "collection_slug": self.title.replace(' ','-').replace('/','-')
        })

    def __str__(self):
        return self.title

class IndexPageContent(models.Model):
    slider_songs = models.ManyToManyField(Song)
    artists = models.ManyToManyField(Singer)
    collections = models.ManyToManyField(Collection)
    special_tags = models.ManyToManyField(Tag)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'صفحه خانه در تاریخ {self.updated_date}'







