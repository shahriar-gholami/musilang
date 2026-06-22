from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class BlogView(View):

    template_name = 'blog/blog.html'

    def get(self, request):
        posts = BlogPost.objects.filter(published=True)
        categories = BlogCategory.objects.all()
        tags = BlogTag.objects.all()[0:10]
        items_per_page = 12
        paginator = Paginator(posts, items_per_page)
        page = request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {
                                              'posts':posts,
                                              'categories':categories,
                                              'tags':tags,
                                              })
    
class BlogCategoryPostsView(View):

    template_name = 'blog/blog_category.html'

    def get(self, request, category_id, category_slug):
        category = get_object_or_404(BlogCategory, id=category_id)
        categories = BlogCategory.objects.all()
        tags = BlogTag.objects.all()[0:10]
        posts = BlogPost.objects.filter(category=category)
        items_per_page = 12
        paginator = Paginator(posts, items_per_page)
        page = request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {
                                                'category':category,
                                                'posts':posts,
                                                'categories':categories,
                                                'tags':tags,
                                                })
    
class BlogTagPostsView(View):
    template_name = 'blog/blog_tag.html'

    def get(self, request, tag_id, tag_slug):
        items_per_page = 12
        tag = get_object_or_404(BlogTag, id=tag_id)
        posts = BlogPost.objects.filter(tags=tag)
        categories = BlogCategory.objects.all()
        tags = BlogTag.objects.all()[0:10]
        paginator = Paginator(posts, items_per_page)
        page = request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {
            'tag': tag,
            'posts': posts,
            'categories':categories,
            'tags':tags,
        })

class BlogPostDetailView(View):

    template_name = "blog/blog-detail.html"

    def get(self, request, post_slug):

        post = get_object_or_404(
            BlogPost,
            slug=post_slug
        )

        categories = BlogCategory.objects.all()
        tags = BlogTag.objects.all()
        posts = BlogPost.objects.order_by('-created_date')[:5]


        return render(request, self.template_name, {
            'categories': categories,
            'tags': tags,
            'post': post,
            'posts': posts,
        })

