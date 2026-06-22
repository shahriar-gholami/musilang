from django.contrib import admin
from .models import Logo, ContactMessage, Faq, MainInfo


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('id', 'wide_logo', 'icon')
    readonly_fields = ('get_wide_logo_url', 'get_icon_url')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'created', 'is_answered')
    list_filter = ('is_answered', 'created')
    search_fields = ('full_name', 'email', 'subject', 'message')
    readonly_fields = ('created',)
    ordering = ('-created',)


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
    search_fields = ('question', 'answer')


@admin.register(MainInfo)
class MainInfoAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'domain', 'email', 'phone')
    search_fields = (
        'site_name',
        'domain',
        'email',
        'phone',
        'seo_title',
        'meta_description',
    )
    list_filter = ('logo',)

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'domain',
                'logo',
                'site_name',
                'about_page_description',
                'footer_description',
                'policies',
            )
        }),
        ('اطلاعات تماس', {
            'fields': (
                'phone',
                'email',
            )
        }),
        ('شبکه‌های اجتماعی', {
            'fields': (
                'instagram',
                'telegram',
                'linkedin',
                'whatsapp',
                'aparat',
                'youtube',
                'twitter',
                'bale',
                'rubika',
            )
        }),
        ('سئو', {
            'fields': (
                'seo_title',
                'meta_description',
            )
        }),
    )
