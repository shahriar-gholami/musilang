from django import forms
from django.contrib.auth import get_user_model
from accounts.models import Customer
from musics.models import Song, Playlist
from .models import *
User = get_user_model()


class PlaylistCreateForm(forms.ModelForm):
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.select_related("singer").all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="آهنگ‌ها",
    )

    class Meta:
        model = Playlist
        fields = ["title", "songs"]
        labels = {
            "title": "نام پلی‌لیست",
            "songs": "آهنگ‌ها",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "مثلاً آهنگ‌های مورد علاقه من",
            }),
        }

from accounts.models import User

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "نام و نام خانوادگی",
            }),
            "email": forms.EmailInput(attrs={
                "class": "dashboard-input",
                "placeholder": "example@email.com",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "dashboard-input",
                "readonly": "readonly",
            }),
        }
        labels = {
            "full_name": "نام و نام خانوادگی",
            "email": "ایمیل",
            "phone_number": "شماره موبایل",
        }

    def clean_phone_number(self):
        # شماره موبایل در این صفحه فقط نمایشی است و تغییر نمی‌کند.
        return self.instance.phone_number


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "favorite_songs",
            "favorite_artists",
            "favorite_collections",
        ]
        labels = {
            "favorite_songs": "آهنگ‌های مورد علاقه",
            "favorite_artists": "خواننده‌های مورد علاقه",
            "favorite_collections": "کالکشن‌های مورد علاقه",
        }
        widgets = {
            "favorite_songs": forms.CheckboxSelectMultiple,
            "favorite_artists": forms.CheckboxSelectMultiple,
            "favorite_collections": forms.CheckboxSelectMultiple,
        }


class SongRequestForm(forms.ModelForm):
    class Meta:
        model = SongRequest
        fields = ["singer_name", "song_name"]

        labels = {
            "singer_name": "نام خواننده",
            "song_name": "نام آهنگ",
        }

        widgets = {
            "singer_name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "مثلاً: محسن چاوشی",
            }),
            "song_name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "مثلاً: کجایی",
            }),
        }

class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "موضوع تیکت",
            }),
            "body": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": "متن درخواست خود را بنویسید...",
                "rows": 5,
            }),
        }
        labels = {
            "subject": "موضوع",
            "body": "متن تیکت",
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "class": "dashboard-textarea ticket-reply-textarea",
                "placeholder": "پاسخ خود را بنویسید...",
                "rows": 3,
            }),
        }
        labels = {
            "body": "پاسخ",
        }


class CommentForm(forms.Form):
    content = forms.CharField(
        label="متن دیدگاه",
        widget=forms.Textarea(attrs={
            "class": "dashboard-textarea",
            "placeholder": "دیدگاه خود را بنویسید",
            "rows": 5,
        }),
    )


