from django.urls import path
from .views import *

app_name = "musics"

urlpatterns = [
    path("create-song/", SongCreateAPIView.as_view(), name="song_create_api"),
    path("songs-create-options/", SongCreateOptionsAPIView.as_view(), name="song_create_options_api"),

]
