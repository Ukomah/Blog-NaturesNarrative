from django.urls import path
from . import views
from .feeds import LatestPostsFeed
from django.views.generic import TemplateView



app_name = 'blog'

urlpatterns = [
    # post views
    # path('', views.post_list, name='post_list'),
    path('', views.PostListView.as_view(), name='post_list'),
    path('posts/tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_details, name='post_details'),
    path('<int:post_id>/share/',views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('about/', TemplateView.as_view(template_name='blog/about.html'), name='about'),
    path('contact/', views.contact_view, name='contact'),
]