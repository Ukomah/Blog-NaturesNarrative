from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


# Create your models here.

## custom manager to retrieve PUBLISHED posts using Post.published.all()
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)
    

    
## Post model to store blog post
class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PD', 'published'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique_for_date='published')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'blog_posts')
    image  = models.ImageField(blank=True, null=True, upload_to='images/')
    body = models.TextField()
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    objects = models.Manager()                          # The default manager
    published_blogs = PublishedManager()                # Customized manager
    tags = TaggableManager()
    



    class Meta:
        ordering = ['-published']
        indexes = [models.Index(fields=['-published'])]


    def __str__(self):                  # displays object readbale name in admin site 
        return self.title
    

    def get_absolute_url(self):
        return reverse('blog:post_details', args=[self.published.year,
                                                  self.published.month,
                                                  self.published.day,
                                                  self.slug])
    

## Tis is used to associate multiple images to a post
class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.post.title
    


## Comment section model to store blog post comments
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['created'])]

    def __str__(self):
        return f'comment by {self.name} on {self.post}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'message from {self.name}'