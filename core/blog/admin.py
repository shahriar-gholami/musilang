from django.contrib import admin
from django.utils.html import format_html
from .models import *

# ثبت مدل BlogCategory
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}  # خودکار پر کردن slug بر اساس name
    ordering = ('name',)

# ثبت مدل BlogTag
@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}  # خودکار پر کردن slug بر اساس name
    ordering = ('name',)

class PostFAQInline(admin.TabularInline):
    model = PostFAQ
    extra = 1
    fields = ('question', 'answer')

# ثبت مدل BlogPost
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_tags', 'published', 'shamsi_created_date', 'display_image')
    list_filter = ('published', 'category', 'tags', 'created_date')
    search_fields = ('title', 'meta_description', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}  # خودکار پر کردن slug بر اساس title
    ordering = ('-created_date',)
    list_editable = ('published',)
    list_select_related = ('category',)
    inlines = [PostFAQInline]
    autocomplete_fields = ('category', 'tags')  # برای انتخاب راحت‌تر دسته‌بندی و تگ‌ها
    filter_horizontal = ('tags',)  # برای مدیریت بهتر رابطه ManyToMany
    

    def display_image(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'تصویر'

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'تگ‌ها'

    def shamsi_created_date(self, obj):
        return obj.shamsi_created_date
    shamsi_created_date.short_description = 'تاریخ ایجاد (شمسی)'