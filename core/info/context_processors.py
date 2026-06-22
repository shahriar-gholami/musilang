# from urllib.parse import urlparse
# from django.contrib.auth.models import AnonymousUser
from info.models import *
# from blog.models import BlogTag
# from accounts.models import Marketer
# from django.contrib.sites.models import Site
# from orders.models import Package

def base_template_context(request):
    info = MainInfo.objects.first()
    # white_pkg = Package.objects.filter(name='3 ماهه').first()
    # yellow_pkg = Package.objects.filter(name='6 ماهه').first()
    # green_pkg = Package.objects.filter(name='1 ساله').first()
    # is_marketer = False
    # logo = Logo.objects.first().wide_logo.url.split('?')[0]
    # favicon = Logo.objects.first().icon.url.split('?')[0]
    # site_name = Site.objects.get_current().name
    # domain = Site.objects.get_current().domain


    return {
            'info' : info,
            # 'logo':logo,
            # 'post_tags':BlogTag.objects.all()[:30],
            # 'favicon':favicon,
            # 'is_marketer':is_marketer,
            # 'site_name':site_name,
            # 'domain':domain,
            # 'white_pkg': white_pkg,
            # 'yellow_pkg': yellow_pkg,
            # 'green_pkg': green_pkg,

        }
 