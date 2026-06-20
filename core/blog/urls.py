from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from . import views


app_name = 'blog'

urlpatterns = [ 
    
    path('', views.BlogView.as_view(), name='post_list'),
    path('category/<int:category_id>/<str:category_slug>/', views.BlogCategoryPostsView.as_view(), name='category_post_list'),
    path('posts/tag/<int:tag_id>/<str:tag_slug>/', views.BlogTagPostsView.as_view(), name='tag_post_list'),
    path('<str:post_slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
]