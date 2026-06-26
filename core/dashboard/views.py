from django.views import View
from musics.models import Playlist, Comment
from accounts.models import Customer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from .models import Ticket, TicketReply
from .forms import *
from django.http import JsonResponse


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
            "favorite_songs": customer.favorite_songs.select_related("singer") if customer else [],
            "favorite_artists": customer.favorite_artists.all() if customer else [],
            "favorite_collections": customer.favorite_collections.all() if customer else [],
        }

        return render(request, self.template_name, context)

    



class DashboardFavoriteRemoveView(LoginRequiredMixin, View):
    def post(self, request, item_type, pk):
        customer = Customer.objects.filter(user=request.user).first()

        if customer is None:
            return JsonResponse(
                {"ok": False, "message": "پروفایل کاربری پیدا نشد."},
                status=400,
            )

        favorite_fields = {
            "song": customer.favorite_songs,
            "artist": customer.favorite_artists,
            "collection": customer.favorite_collections,
        }

        favorite_manager = favorite_fields.get(item_type)

        if favorite_manager is None:
            return JsonResponse(
                {"ok": False, "message": "نوع علاقه‌مندی نامعتبر است."},
                status=400,
            )

        favorite_manager.remove(pk)

        return JsonResponse({
            "ok": True,
            "message": "آیتم از علاقه‌مندی‌ها حذف شد.",
        })



class DashboardPlaylistsView(LoginRequiredMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        playlists = Playlist.objects.filter(customer=customer).prefetch_related("songs").order_by("-created_date")
        return render(request, "dashboard/playlists.html", {"playlists": playlists})


class PlaylistDetailView(View):
    template_name = "dashboard/playlist_detail.html"

    def get(self, request, pk, playlist_slug):
        collection = get_object_or_404(Playlist, id=pk)
        songs = list(collection.songs.all())

        can_manage_playlist = False

        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()

            if customer and collection.customer_id == customer.id:
                can_manage_playlist = True

        return render(request, self.template_name, {
            "collection": collection,
            "songs": songs,
            "can_manage_playlist": can_manage_playlist,
        })


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
        form = SongRequestForm()

        user_requests = SongRequest.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

        return render(request, self.template_name, {
            "form": form,
            "user_requests": user_requests,
        })

    def post(self, request):
        form = SongRequestForm(request.POST)

        if form.is_valid():
            song_request = form.save(commit=False)
            song_request.user = request.user
            song_request.save()

            messages.success(
                request,
                "درخواست آهنگ شما با موفقیت ثبت شد و پس از بررسی اضافه می‌شود."
            )

            return redirect("dashboard:dashboard_song_request")

        user_requests = SongRequest.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

        messages.error(request, "لطفاً اطلاعات فرم را درست وارد کنید.")

        return render(request, self.template_name, {
            "form": form,
            "user_requests": user_requests,
        })


class DashboardAccountView(LoginRequiredMixin, View):
    template_name = "dashboard/account.html"

    def get_customer(self, user):
        customer, created = Customer.objects.get_or_create(user=user)
        return customer

    def get(self, request, *args, **kwargs):
        customer = self.get_customer(request.user)
        form = AccountUpdateForm(instance=request.user)

        context = {
            "form": form,
            "customer": customer,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        customer = self.get_customer(request.user)
        form = AccountUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات حساب شما با موفقیت به‌روزرسانی شد.")
            return redirect("dashboard:dashboard_account")

        context = {
            "form": form,
            "customer": customer,
        }
        return render(request, self.template_name, context)


class DashboardTicketsView(LoginRequiredMixin, View):
    template_name = "dashboard/tickets.html"

    def get_customer(self, user):
        customer, created = Customer.objects.get_or_create(user=user)
        return customer

    def get_tickets(self, customer):
        return (
            Ticket.objects
            .filter(customer=customer)
            .prefetch_related("replies")
            .order_by("-created_date")
        )

    def get_context_data(self, request, create_form=None, reply_form=None):
        customer = self.get_customer(request.user)

        return {
            "tickets": self.get_tickets(customer),
            "create_form": create_form or TicketCreateForm(),
            "reply_form": reply_form or TicketReplyForm(),
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        customer = self.get_customer(request.user)
        action = request.POST.get("action")

        if action == "create_ticket":
            return self.create_ticket(request, customer)

        if action == "reply_ticket":
            return self.reply_ticket(request, customer)

        if action == "close_ticket":
            return self.close_ticket(request, customer)

        messages.error(request, "درخواست نامعتبر است.")
        return redirect("dashboard_tickets")

    def create_ticket(self, request, customer):
        form = TicketCreateForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.customer = customer
            ticket.save()
            messages.success(request, "تیکت شما با موفقیت ثبت شد.")
            return redirect("dashboard:dashboard_tickets")

        context = self.get_context_data(request, create_form=form)
        return render(request, self.template_name, context)

    def reply_ticket(self, request, customer):
        ticket = get_object_or_404(
            Ticket,
            id=request.POST.get("ticket_id"),
            customer=customer,
        )

        if ticket.is_closed:
            messages.error(request, "این تیکت بسته شده و امکان ارسال پاسخ ندارد.")
            return redirect("dashboard:dashboard_tickets")

        form = TicketReplyForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.main_ticket = ticket
            reply.save()

            # بعد از پاسخ کاربر، تیکت دوباره در وضعیت نیازمند پاسخ قرار می‌گیرد.
            ticket.is_answered = False
            ticket.save(update_fields=["is_answered"])

            messages.success(request, "پاسخ شما با موفقیت ثبت شد.")
            return redirect("dashboard:dashboard_tickets")

        context = self.get_context_data(request, reply_form=form)
        return render(request, self.template_name, context)

    def close_ticket(self, request, customer):
        ticket = get_object_or_404(
            Ticket,
            id=request.POST.get("ticket_id"),
            customer=customer,
        )

        ticket.is_closed = True
        ticket.save(update_fields=["is_closed"])

        messages.success(request, "تیکت با موفقیت بسته شد.")
        return redirect("dashboard:dashboard_tickets")


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

    def get(self, request, *args, **kwargs):
        comments = (
            Comment.objects
            .filter(user=request.user)
            .select_related("song")
            .order_by("-created_at")
        )

        context = {
            "comments": comments,
        }
        return render(request, self.template_name, context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from accounts.models import Customer
from musics.models import Playlist, Song


class DashboardPlaylistSongRemoveView(LoginRequiredMixin, View):
    def post(self, request, playlist_pk, song_pk):
        customer = get_object_or_404(Customer, user=request.user)

        playlist = get_object_or_404(
            Playlist,
            pk=playlist_pk,
            customer=customer,
        )

        song = get_object_or_404(Song, pk=song_pk)

        if not playlist.songs.filter(pk=song.pk).exists():
            return JsonResponse({
                "ok": False,
                "message": "این آهنگ در پلی‌لیست وجود ندارد.",
            }, status=400)

        playlist.songs.remove(song)

        songs_count = playlist.songs.count()

        return JsonResponse({
            "ok": True,
            "message": "آهنگ از پلی‌لیست حذف شد.",
            "songs_count": songs_count,
        })
