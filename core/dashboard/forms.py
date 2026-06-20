from django import forms
from django.contrib.auth import get_user_model
from accounts.models import Customer
from musics.models import Song
from musics.models import Playlist

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
        fields = ["name", "songs"]
        labels = {
            "name": "نام پلی‌لیست",
            "songs": "آهنگ‌ها",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "مثلاً آهنگ‌های مورد علاقه من",
            }),
        }


class AccountUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        label="نام",
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": "نام",
        }),
    )
    last_name = forms.CharField(
        required=False,
        label="نام خانوادگی",
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": "نام خانوادگی",
        }),
    )
    email = forms.EmailField(
        required=False,
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            "class": "dashboard-input",
            "placeholder": "email@example.com",
        }),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


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


class SongRequestForm(forms.Form):
    song_title = forms.CharField(
        label="نام آهنگ",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": "نام آهنگ را وارد کنید",
        }),
    )
    singer_name = forms.CharField(
        label="نام خواننده",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": "نام خواننده",
        }),
    )
    description = forms.CharField(
        label="توضیحات",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "dashboard-textarea",
            "placeholder": "اگر توضیحی درباره آهنگ دارید بنویسید",
            "rows": 5,
        }),
    )


class TicketCreateForm(forms.Form):
    title = forms.CharField(
        label="عنوان تیکت",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": "عنوان تیکت",
        }),
    )
    message = forms.CharField(
        label="متن پیام",
        widget=forms.Textarea(attrs={
            "class": "dashboard-textarea",
            "placeholder": "متن پیام خود را بنویسید",
            "rows": 6,
        }),
    )


class CommentForm(forms.Form):
    content = forms.CharField(
        label="متن دیدگاه",
        widget=forms.Textarea(attrs={
            "class": "dashboard-textarea",
            "placeholder": "دیدگاه خود را بنویسید",
            "rows": 5,
        }),
    )


