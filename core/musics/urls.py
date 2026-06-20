from django.urls import path

from . import views

app_name = "musics"

urlpatterns = [
    # Home
    path("", views.IndexPageView.as_view(), name="index"),
    path("songs/", views.SongListView.as_view(), name="songs_list"),
    path("songs/<int:pk>/<str:song_slug>/", views.SingleSongDetailView.as_view(), name="song_detail"),
    path("songs/category/<slug:slug>/", views.SongsListByCategoryView.as_view(), name="songs_by_category",),
    path("songs/tag/<int:tag_id>/<str:tag_slug>/", views.SongsListByTagView.as_view(),name="songs_by_tag",),
    path("songs/language/<str:code>/",views.SongsListByLanguage.as_view(),name="songs_by_language",),
    path("search/", views.SearchView.as_view(), name="search"),
    path("collections/",views.CollectionListView.as_view(),name="collection_list"),
    path("collections/<int:pk>/<str:collection_slug>/",views.CollectionDetailView.as_view(),name="collection_detail"),
    path("artists/", views.ArtistListView.as_view(), name="artist_list"),
    path("artists/<int:pk>/<slug:artist_slug>/", views.ArtistDetailView.as_view(), name="artist_detail"),
     path("albums/", views.AlbumListView.as_view(), name="album_list"),
    path("albums/<int:pk>/<slug:album_slug>/", views.AlbumDetailView.as_view(), name="album_detail"),
path("songs/create-comment/<int:pk>/",views.CreateSongCommentView.as_view(), name="song_comment_create"),
    path("songs/submit_rating/<int:pk>/",views.CreateSongRatingView.as_view(), name="song_rating_create"),

]
