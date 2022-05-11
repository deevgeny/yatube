import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=''
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.author)

    def test_create_new_post_without_group(self):
        """Create new post without group."""
        # Prepare test data
        posts_count = Post.objects.count()
        form_data = {
            'text': 'New post',
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Run test
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.author.username}
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            ('Incorrect total number of posts in database after create '
             f'operation: {posts_count} post(s) before vs '
             f'{Post.objects.count()} post(s) after, absolute difference = '
             f'{abs(Post.objects.count() - posts_count)}')

        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.author,
                text=form_data['text'],
                group=None
            ).exists(),
            'New post without group does not exist in database'
        )

    def test_create_new_post_with_group(self):
        """Create new post with group."""
        # Prepare test data
        posts_count = Post.objects.count()
        form_data = {
            'text': 'New post with group',
            'group': PostFormTests.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Run test
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.author.username}
            )
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            ('Incorrect total number of posts in database after create '
             f'operation: {posts_count} post(s) before vs '
             f'{Post.objects.count()} post(s) after, absolute difference = '
             f'{abs(Post.objects.count() - posts_count)}')
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.author,
                text=form_data['text'],
                group=PostFormTests.group
            ).exists(),
            'New post with group does not exist in database'
        )

    def test_edit_post(self):
        """Edit post."""
        # Prepare test data
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Edited text',
            'group': PostFormTests.group.id
        }
        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        # Run test
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostFormTests.post.id}
            )
        )
        self.assertEqual(
            Post.objects.get(pk=PostFormTests.post.id).text,
            form_data['text'],
            'Post text was not edited in database'
        )
        self.assertEqual(
            Post.objects.get(pk=PostFormTests.post.id).group,
            PostFormTests.group,
            'Post group was not edited in database'
        )
        self.assertTrue(
            Post.objects.count() == posts_count,
            ('Total number of posts in database changed after edit operation: '
             f'{posts_count} post(s) before vs '
             f'{Post.objects.count()} post(s) after, absolute difference = '
             f'{abs(Post.objects.count() - posts_count)}')
        )

    def test_create_new_post_with_image(self):
        """Create new post with image."""
        # Prepare test data
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Post with image',
            'image': uploaded,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Run test
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.author.username}
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            ('Incorrect total number of posts in database after create '
             f'operation: {posts_count} post(s) before vs '
             f'{Post.objects.count()} post(s) after, absolute difference = '
             f'{abs(Post.objects.count() - posts_count)}')
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.author,
                text=form_data['text'],
                image='posts/small.gif',
                group=None
            ).exists(),
            'New post with image does not exist in database'
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Post with comment'
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(CommentFormTests.author)

    def test_add_new_comment(self):
        """Add new comment to post."""
        # Prepare test data
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'New comment',
            'author': CommentFormTests.author,
            'post': CommentFormTests.post
        }
        response = self.author_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        # Run test
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': CommentFormTests.post.id}
            ),
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            ('Incorrect total number of comments in database after add '
             f'operation: {comments_count} comment(s) before vs '
             f'{Comment.objects.count()} comment(s) after, absolute '
             f'difference = {abs(Comment.objects.count() - comments_count)}')
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=form_data['author'],
                post=form_data['post'],
            ).exists(),
            'New comment does not exist in database'
        )
