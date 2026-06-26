from django.urls import path

from .views import *

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("dashboard/favorites/", DashboardFavoritesView.as_view(), name="dashboard_favorites"),
    path("dashboard/playlists/", DashboardPlaylistsView.as_view(), name="dashboard_playlists"),
    path("playlists/remove/<int:playlist_pk>/songs/<int:song_pk>/",DashboardPlaylistSongRemoveView.as_view(),name="playlist_song_remove",),
    path("dashboard/playlists/create/",DashboardPlaylistCreateView.as_view(),name="dashboard_playlist_create",),    
    path("dashboard/playlists/<int:pk>/<str:playlist_slug>/", PlaylistDetailView.as_view(), name="playlist_detail"),
    path("favorites/remove/<str:item_type>/<int:pk>/",DashboardFavoriteRemoveView.as_view(),name="favorite_remove",),
    path("dashboard/song-request/", DashboardSongRequestView.as_view(), name="dashboard_song_request"),
    path("dashboard/account/", DashboardAccountView.as_view(), name="dashboard_account"),
    path("dashboard/tickets/", DashboardTicketsView.as_view(), name="dashboard_tickets"),
    path("dashboard/packages/", DashboardPackagesView.as_view(), name="dashboard_packages"),
    path("dashboard/comments/", DashboardCommentsView.as_view(), name="dashboard_comments"),
]
