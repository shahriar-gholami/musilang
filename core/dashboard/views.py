from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from musics.models import Playlist
from accounts.models import Customer

from .forms import PlaylistCreateForm


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard/index.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()

        context = {
            "customer": customer,
            "favorite_songs_count": customer.favorite_songs.count(),
            "favorite_artists_count": customer.favorite_artists.count(),
            "favorite_collections_count": customer.favorite_collections.count(),
            "favorite_songs": customer.favorite_songs.select_related("singer")[:5],
        }

        return render(request, self.template_name, context)


class DashboardFavoritesView(LoginRequiredMixin, View):
    template_name = "dashboard/favorites.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()

        context = {
            "customer": customer,
            "favorite_songs": customer.favorite_songs.select_related("singer"),
            "favorite_artists": customer.favorite_artists.all(),
            "favorite_collections": customer.favorite_collections.all(),
        }

        return render(request, self.template_name, context)


class DashboardPlaylistsView(LoginRequiredMixin, View):
    template_name = "dashboard/playlists.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()

        context = {
            "customer": customer,
            "playlists": customer.playlist_set.prefetch_related("songs"),
        }

        return render(request, self.template_name, context)


class DashboardPlaylistCreateView(LoginRequiredMixin, View):
    template_name = "dashboard/playlist_create.html"

    def get(self, request):
        form = PlaylistCreateForm()
        customer = Customer.objects.filter(user=request.user).first()
        context = {
            "form": form,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        form = PlaylistCreateForm(request.POST)

        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.customer = customer
            playlist.save()
            form.save_m2m()

            return redirect("dashboard:dashboard_playlists")

        context = {
            "form": form,
        }

        return render(request, self.template_name, context)


class DashboardSongRequestView(LoginRequiredMixin, View):
    template_name = "dashboard/song_request.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request):
        # بعدا اگر مدل SongRequest ساختی، اینجا ذخیره می‌شود.
        return redirect("accounts:dashboard_song_request")


class DashboardAccountView(LoginRequiredMixin, View):
    template_name = "dashboard/account.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()

        context = {
            "customer": customer,
            "user": request.user,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        # بعدا اگر فرم ویرایش حساب ساختی، اینجا هندل می‌شود.
        return redirect("accounts:dashboard_account")


class DashboardTicketsView(LoginRequiredMixin, View):
    template_name = "dashboard/tickets.html"

    def get(self, request):
        context = {
            "tickets": [],
        }

        return render(request, self.template_name, context)


class DashboardPackagesView(LoginRequiredMixin, View):
    template_name = "dashboard/packages.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()

        context = {
            "customer": customer,
            "packages": [],
        }

        return render(request, self.template_name, context)


class DashboardCommentsView(LoginRequiredMixin, View):
    template_name = "dashboard/comments.html"

    def get(self, request):
        context = {
            "comments": [],
        }

        return render(request, self.template_name, context)
