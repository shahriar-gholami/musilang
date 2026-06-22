from django.db import models
from khayyam import JalaliDatetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.templatetags.static import static
from datetime import date
from django_jalali.db import models as jmodels
import jdatetime
from django.db import models
from ckeditor.fields import RichTextField
from musics.models import Tag, Language, Category, Singer
import os
import uuid


# تابع مدیریت مسیر آپلود
def upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    folder = instance.__class__.__name__.lower()
    return f"music/{folder}/{uuid.uuid4().hex}{ext}"


class Logo(models.Model):
    wide_logo = models.ImageField(upload_to=upload_to, default='media/11.png')
    icon = models.ImageField(upload_to=upload_to, default='media/11.png')

    def get_wide_logo_url(self):
        return self.wide_logo.url.split('?')[0]
    
    def get_icon_url(self):
        return self.icon.url.split('?')[0]

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=250)
    message = models.TextField(default = "پیام خود را وارد نمایید.")
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_answered = models.BooleanField(default = False)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'{self.full_name} - {self.subject}'

class Faq(models.Model):
    question = models.TextField()
    answer = models.TextField()
    
class MainInfo(models.Model):
    domain = models.CharField(max_length=1024, null=True, blank=True)
    logo = models.ForeignKey(Logo, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=1024, null=True, blank=True)
    about_page_description = RichTextField(default = "insert the post body", null=True, blank=True)
    footer_description = models.TextField(null=True, blank=True)
    policies = RichTextField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    telegram = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    aparat = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    bale = models.CharField(max_length=255, null=255, blank=True)
    rubika = models.CharField(max_length=255, null=255, blank=True)
    seo_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    
    def get_tags(self):
        return Tag.objects.filter(is_special=True)
    
    def get_categories(self):
        return Category.objects.all()
    
    def get_languages(self):
        return Language.objects.all()
    
    def get_singers(self):
        return Singer.objects.filter(is_special=True)

    def save(self, *args, **kwargs):
        self.about_page_description = self.about_page_description.replace('\n','<br>')
        self.footer_description = self.footer_description.replace('\n','<br>')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'اطلاعات مهم سایت {self.site_name}'