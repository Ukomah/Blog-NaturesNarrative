from django.test import TestCase
from .models import Post, PostImage, Comment, ContactMessage
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

# Create your tests here.

# Test for the Post model
class PostModelTest(TestCase):

    def setUp(self):
        # Create a User for the author
        self.author = User.objects.create(username='testuser')


    def test_post_model_exists(self):
        posts = Post.objects.count()

        self.assertEqual(posts, 0)


    def test_model_has_string_representation(self):
        post = Post.objects.create(title='First post', author=self.author)

        self.assertEqual(str(post), post.title)


# Test for the Post model
class PostImageModelTest(TestCase):
    def setUp(self):
        # Create a User for the author
        self.author = User.objects.create(username='testuser')

    def test_post_image_model_exists(self):
        post_images = PostImage.objects.count()
        self.assertEqual(post_images, 0)

    def test_model_has_string_representation(self):
        # Create a Post
        post = Post.objects.create(title='First post', author=self.author)

        # Create a SimpleUploadedFile for a test image
        image = SimpleUploadedFile("test_image.jpg", b"file_content")

        # Create a PostImage associated with the Post and image
        post_image = PostImage.objects.create(post=post, image=image)

        # Verify that the string representation of the PostImage matches the Post title
        self.assertEqual(str(post_image), post.title)



class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a User object with ID 1
        cls.author = User.objects.create(username='testuser')

        # Create a Post for testing, as Comment requires a ForeignKey to Post
        cls.post = Post.objects.create(title='Test Post', author_id=cls.author.id)

    def test_comment_creation(self):
        # Create a Comment
        comment = Comment.objects.create(
            post=self.post,
            name='John Doe',
            email='johndoe@example.com',
            body='This is a test comment',
        )

        # Check if the Comment object was created successfully
        self.assertIsInstance(comment, Comment)

    def test_comment_string_representation(self):
        # Create a Comment
        comment = Comment.objects.create(
            post=self.post,
            name='Jane Smith',
            email='janesmith@example.com',
            body='Another test comment',
        )

        # Check if the string representation of the Comment matches the name
        self.assertEqual(str(comment), f'comment by {comment.name} on {comment.post.title}')


    def test_comment_defaults(self):
        # Create a Comment without specifying any fields
        comment = Comment.objects.create(post=self.post)

        # Check if the default values are set correctly
        self.assertEqual(comment.name, '')
        self.assertEqual(comment.email, '')
        self.assertEqual(comment.body, '')
        self.assertTrue(comment.active)

    def test_comment_ordering(self):
        # Create multiple Comments with different creation timestamps
        comment1 = Comment.objects.create(post=self.post, name='Comment 1')
        comment2 = Comment.objects.create(post=self.post, name='Comment 2')

        # Check if ordering is based on the 'created' field (descending)
        comments = Comment.objects.filter(post=self.post)
        self.assertEqual(comments[0], comment2)
        self.assertEqual(comments[1], comment1)



class ContactModelTest(TestCase):
  
    def test_contact_creation(self):
        current_time = timezone.now()
        # Create a Contact message
        contact = ContactMessage.objects.create(
            name='John Doe',
            email='johndoe@example.com',
            body='This is a test comment',
        )

        created_time = contact.created

        # Get the actual created time from the ContactMessage object
        time_delta = current_time - created_time

        # Check if the Comment object was created successfully
        self.assertLessEqual(time_delta.total_seconds(), 1)
        self.assertIsInstance(contact, ContactMessage)


    def test_string_representation(self):
        # Create a ContactMessage
        contact = ContactMessage.objects.create(
                name='Jane Smith',
                email='janesmith@example.com',
                body='Another test message',
        )

        # Check if the string representation matches the expected format
        self.assertEqual(str(contact), f'message from {contact.name}')

    def test_defaults(self):
        # Create a ContactMessage without specifying any fields

        contact = ContactMessage.objects.create()

        # Check if default values are set correctly
        self.assertEqual(contact.name, '')
        self.assertEqual(contact.email, '')
        self.assertEqual(contact.body, '')
    


class PostListViewTest(TestCase):
    @classmethod

    def setUpTestData(self):
        # Create a User for the author
        self.author = User.objects.create(username='testuser')
        number_of_posts = 10

        for post_num in range(number_of_posts):
             
              # Create a SimpleUploadedFile for a test image
            image = SimpleUploadedFile("test_image.jpg", b"file_content")

            Post.objects.create(
                title=f'Test Post {post_num}',
                slug=f'test-post-{post_num}',
                image=image,
                author=self.author,  # Replace with a valid user ID
                body=f'Test content for Post {post_num}',
                status=Post.Status.PUBLISHED,
            )

    def test_view_url_exists_at_root(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

