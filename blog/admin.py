from django.contrib import admin
from .models import Post, Comment, PostImage

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'published', 'status']
    list_filter  = ['status', 'created', 'published', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published'
    ordering = ['status', 'published']



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'post']
    


