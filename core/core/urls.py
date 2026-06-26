from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from musics.sitemaps import sitemaps


# from . import views

urlpatterns = [
    path('blog/', include("blog.urls")),
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('dashboard/', include("dashboard.urls")),
    path('orders/', include("orders.urls")),
    path('', include("musics.urls")),
    path('landings/', include("landings.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# serving static and media for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

