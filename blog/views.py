from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Comment
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.db.models import Count
from taggit.models import Tag
from django.contrib.postgres.search import SearchVector
from .forms import EmailPostForm, CommentForm, SearchForm, ContactForm
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.http import HttpResponseRedirect
from django.urls import reverse

## A view to display all published blogs from the database on request
# def post_list(request):
#     post_list = Post.published_blogs.all()

#     # Pagination with 6 posts per page
#     paginator = Paginator(post_list, 6)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         # if page_number is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         # if page is not an integer, deleiver the first page
#         posts = paginator.page(1)

#     return render(request, 'blog/post/list.html', {'posts':posts})



# class to list all blog post
class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published_blogs.annotate(num_comments=Count('comments')).order_by('-published').all()
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        qs = super().get_queryset()  # gets the initial queryset defined above
        
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            qs = qs.filter(tags__in=[tag])
            
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adding tag to the context, if tag_slug is provided
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        
        # Adding tags with post count to the context
        context['tags'] = Tag.objects.filter(post__in=self.get_queryset()).annotate(num_posts=Count('post')).distinct()
        
        return context
    


## A view to display the details of a particular blog post from the database on request
def post_details(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             published__year=year,
                             published__month=month,
                             published__day=day)
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users comment
    form = CommentForm()

    # Adding tags with post count to the context
    tags = Tag.objects.filter(post__in=Post.published_blogs.all()).annotate(num_posts=Count('post')).distinct()
    
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published_blogs.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:4]

    return render(request, 'blog/post/details.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts, 'tags': tags})




# class to display form for sharing a blog, and manage its submission
def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    # Initialize sent to False
    sent = False

    if request.method == 'POST':
        #Forms was submitted
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # forms fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n {cd['name']}\'s comments: {cd['comments']}" 

            send_mail(subject, message, 'henryukomah@gmail.com', [cd['to']])

            sent = True

    else:

        form = EmailPostForm()

    # Adding tags with post count to the context
    tags = Tag.objects.filter(post__in=Post.published_blogs.all()).annotate(num_posts=Count('post')).distinct()

    return render(request, 'blog/post/share.html', {'post': post, 'form':form, 'sent': sent, 'tags':tags})



# class to handle comment submission
@require_POST
def post_comment(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html', {'post':post, 'form':form, 'comment':comment})




def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            
            # Use SearchVector and SearchRank for full-text search
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            
            # Combine with TrigramSimilarity for fuzzy matching
            title_trigram = TrigramSimilarity('title', query)
            body_trigram = TrigramSimilarity('body', query)
            
            # Annotate the results with search rank and trigram similarity
            results = Post.published_blogs.annotate(
                rank=SearchRank(search_vector, search_query),
                similarity_title=title_trigram,
                similarity_body=body_trigram
            )

            # Filter and order by combined criteria
            results = results.filter(
                Q(rank__gte=0.1) | 
                Q(similarity_title__gt=0.1) | 
                Q(similarity_body__gt=0.1)
            ).order_by('-rank', '-similarity_title', '-similarity_body')

            # Pagination logic
            paginator = Paginator(results, 10)  # Show 10 results per page
            page = request.GET.get('page')

            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver the first page
                results = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver the last page of results
                results = paginator.page(paginator.num_pages)


    return render(request,'blog/post/search.html',{'form': form,'query': query,'results': results})



def contact_view(request):
    sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            body = form.cleaned_data['body']

            # Construct the email message
            subject = 'Blog - Contact Form Submission'
            message = f'Name: {name}\nEmail: {email}\nMessage:\n{body}'

            # Replace 'recipient@example.com' with the email address of the blog owner
            recipient_email = ['henryukomah@gmail.com']

            # Send the email to the blog owner
            send_mail(
                subject,
                message,
                email,  # Use the sender's email as the 'from_email'
                recipient_email,  # Use the recipient's email as the recipient
                fail_silently=False,
            )
            sent = True

            
    else:
        form = ContactForm()

    return render(request, 'blog/contact.html', {'form': form, 'sent':sent})
