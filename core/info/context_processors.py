from info.models import *
from musics.models import Song, Collection
from blog.models import BlogPost


def base_template_context(request):
    info = MainInfo.objects.first()
    top_songs = Song.objects.order_by("-views_count", "-created_at")[:4]
    latest_songs = Song.objects.order_by("-created_at")[:4]
    latest_collections = Collection.objects.order_by("-created_at")[:4]
    # white_pkg = Package.objects.filter(name='3 ماهه').first()
    # yellow_pkg = Package.objects.filter(name='6 ماهه').first()
    # green_pkg = Package.objects.filter(name='1 ساله').first()



    return {
            'info' : info,
            'top_songs': top_songs,
            'footer_latest_songs': latest_songs,
            'latest_collections': latest_collections
            # 'white_pkg': white_pkg,
            # 'yellow_pkg': yellow_pkg,
            # 'green_pkg': green_pkg,

        }
 