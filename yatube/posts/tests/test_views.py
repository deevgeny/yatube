import datetime
import os
import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings, tag
from django.urls import reverse

from ..forms import CommentForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare test data
        # Create image file in temporary test media directory
        cls.test_image_file_name = 'test_image.gif'
        small_gif_bytes = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        with open(
            os.path.join(settings.MEDIA_ROOT, cls.test_image_file_name),
            'wb'
        ) as f:
            f.write(small_gif_bytes)
        # Create records in test database
        # Create authors
        cls.author = User.objects.create_user(username='author')
        cls.other_author = User.objects.create_user(username='other_author')
        # Create followers
        cls.author_follower = User.objects.create_user(
            username='author_follower'
        )
        Follow.objects.create(
            user=cls.author_follower,
            author=cls.author
        )
        cls.other_author_follower = User.objects.create_user(
            username='other_author_follower'
        )
        Follow.objects.create(
            user=cls.other_author_follower,
            author=cls.other_author
        )
        # Create groups
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='Test description'
        )
        cls.other_group = Group.objects.create(
            title='Other group',
            slug='other-group',
            description='Other description'
        )
        # Create posts for specific tests, count = 3
        cls.other_group_post = Post.objects.create(
            author=cls.author,
            text='Other group post',
            group=cls.other_group
        )
        cls.post_with_image = Post.objects.create(
            author=cls.author,
            text='Post with image',
            group=cls.group,
            image=cls.test_image_file_name
        )
        cls.post_with_comment = Post.objects.create(
            author=cls.author,
            text='Post with comment',
        )
        # Create posts for regular tests, count = 12, total: 3 + 12 = 15.
        # Keep count of total to prevent test_paginator_second_page() overflow!
        Post.objects.bulk_create(
            [Post(
                author=cls.author,
                text=f'Test text {i}',
                group=cls.group
            ) for i in range(1, settings.PAGINATOR_LIMIT + 3)
            ]
        )
        # Create post comments
        cls.author_comment = Comment.objects.create(
            post=cls.post_with_comment,
            author=cls.author,
            text='Author comment'
        )
        cls.other_author_comment = Comment.objects.create(
            post=cls.post_with_comment,
            author=cls.other_author,
            text='Other author comment'
        )
        # Prepare posts queryset for tests
        cls.posts = Post.objects.all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.quest_client = Client()
        self.author_client = Client()
        self.author_follower_client = Client()
        self.other_author_follower_client = Client()
        self.author_client.force_login(PostsPageTests.author)
        self.author_follower_client.force_login(PostsPageTests.author_follower)
        self.other_author_follower_client.force_login(
            PostsPageTests.other_author_follower
        )

    def tearDown(self):
        super().tearDown()
        # Clear cache for views with @cache_page() decorator
        cache.clear()

    def test_pages_use_correct_templates(self):
        """URL reverse(namespace:name) uses correct HTML template."""
        # Prepare test data
        reverse_template_map = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostsPageTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsPageTests.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPageTests.posts[0].id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsPageTests.posts[0].id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        # Run test
        for url, template in reverse_template_map.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template
                )

    def test_index_page_context(self):
        """Index page context."""
        # Prepare test data
        error_msg = "Incorrect context['page_obj'] at {}{}"
        url = reverse('posts:index')
        response = self.author_client.get(url)
        # Run test
        self.assertTrue(
            response.context['index'],
            "Incorrect context['index'] value"
        )
        for obj, check in zip(
            response.context['page_obj'],
            PostsPageTests.posts[:settings.PAGINATOR_LIMIT]
        ):
            with self.subTest(obj=obj):
                self.assertEqual(
                    obj,
                    check,
                    error_msg.format(repr(url), '')
                )
                # Additional check for posts with image
                if check.image:
                    self.assertIsNotNone(
                        obj.image,
                        error_msg.format(repr(url), ': post image is None')
                    )
                    self.assertEqual(
                        obj.image.name,
                        PostsPageTests.test_image_file_name,
                        error_msg.format(repr(url), ': wrong image file name')
                    )

    def test_group_page_context(self):
        """Group page context."""
        # Prepare test data
        url = reverse(
            'posts:group_list',
            kwargs={'slug': PostsPageTests.group.slug})
        response = self.author_client.get(url)
        # Run test
        for obj, check in zip(
            response.context['page_obj'],
            PostsPageTests.posts[:settings.PAGINATOR_LIMIT]
        ):
            with self.subTest(obj=obj):
                self.assertEqual(
                    obj,
                    check,
                    f"Incorrect context['page_obj'] at {repr(url)}"
                )
                # Additional check for posts with image
                if check.image:
                    self.assertIsNotNone(
                        obj.image,
                        (f"Incorrect context['page_obj'] at {repr(url)}"
                         ": post image is None")
                    )
                    self.assertEqual(
                        obj.image.name,
                        PostsPageTests.test_image_file_name,
                        (f"Incorrect context['page_obj'] at {repr(url)}"
                         ": wrong image file name")
                    )
        self.assertEqual(
            response.context['group'],
            PostsPageTests.group,
            f"Incorrect context['group'] at {repr(url)}"
        )

    def test_profile_page_context_authorized(self):
        """Profile page context for authorized user."""
        # Prepare test data
        url = reverse(
            'posts:profile',
            kwargs={'username': PostsPageTests.author.username}
        )
        response = self.author_client.get(url)
        # Run test
        for obj, check in zip(
            response.context['page_obj'],
            PostsPageTests.posts[:settings.PAGINATOR_LIMIT]
        ):
            with self.subTest(obj=obj):
                self.assertEqual(
                    obj,
                    check,
                    (f"Incorrect context['page_obj'] at {repr(url)} "
                     "for authorized user")
                )
        self.assertEqual(
            response.context['author'],
            PostsPageTests.author,
            (f"Incorrect context['author'] at {repr(url)} "
             "for authorized user")
        )
        self.assertEqual(
            response.context['posts_count'],
            len(PostsPageTests.posts),
            (f"Incorrect context['posts_count'] at {repr(url)} "
             "for authorized user")
        )
        self.assertFalse(
            response.context['following'],
            (f"Incorrect context['following'] at {repr(url)} "
             "for authorized user")
        )

    def test_profile_page_context_anonymous(self):
        """Profile page context for anonymous user."""
        # Prepare test data
        url = reverse(
            'posts:profile',
            kwargs={'username': PostsPageTests.author.username}
        )
        response = self.quest_client.get(url)
        # Run test
        self.assertIsNone(
            response.context['following'],
            (f"Incorrect context['following'] at {repr(url)} "
             "for anonymous user")
        )

    def test_post_details_page_context(self):
        """Post details page context for authorized user."""
        # Prepare test data
        post_comments = Comment.objects.filter(
            post=PostsPageTests.post_with_comment
        )
        url = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPageTests.post_with_comment.id}
        )
        response = self.author_client.get(url)
        # Run test
        self.assertEqual(
            response.context['post'],
            PostsPageTests.post_with_comment,
            f"Incorrect context['post'] at {repr(url)}"
        )
        self.assertEqual(
            response.context['posts_count'],
            len(PostsPageTests.posts),
            f"Incorrect context['posts_count'] at {repr(url)}"
        )
        self.assertIsInstance(
            response.context['form'],
            CommentForm,
            f"Incorrect context['form'] at {repr(url)}"
        )
        for obj, check in zip(response.context['comments'], post_comments):
            with self.subTest(obj=obj):
                self.assertEqual(
                    obj,
                    check,
                    f"Incorrect context['comments'] at {repr(url)}"
                )

    def test_edit_post_page_context(self):
        """Edit post page context."""
        # Prepare test data
        post_to_check = PostsPageTests.posts[0]
        edit_form_values = {
            'text': post_to_check.text,
            'group': post_to_check.group.id
        }
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': post_to_check.id}
        )
        response = self.author_client.get(url)
        # Run test
        for field_name, check_value in edit_form_values.items():
            with self.subTest(field_name=field_name):
                form_field_value = response.context['form'][field_name].value()
                self.assertEqual(
                    form_field_value, check_value,
                    (f'Incorrect {form_field_value} value '
                     f'in field {repr(field_name)}')
                )

    def test_create_post_page_context(self):
        """Form in create post page context."""
        # Prepare test data
        post_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        response = self.author_client.get(reverse('posts:post_create'))
        # Run test
        for field_name, field_type in post_form_fields.items():
            with self.subTest(field_name=field_name):
                form_field = response.context['form'].fields[field_name]
                self.assertIsInstance(
                    form_field,
                    field_type,
                    (f'Incorrect {type(form_field)} type '
                     f'for field {repr(field_name)}')
                )

    def test_paginator_first_page(self):
        """Paginator first page."""
        # Prepare test data
        response = self.author_client.get(reverse('posts:index'))
        # Run test
        self.assertEqual(
            len(response.context['page_obj']),
            settings.PAGINATOR_LIMIT,
            'Incorrect number of posts on first page.'
        )

    def test_paginator_second_page(self):
        """Paginator second page."""
        # Prepare test data
        response = self.author_client.get(reverse('posts:index') + '?page=2')
        # Run test
        self.assertEqual(
            len(response.context['page_obj']),
            len(PostsPageTests.posts) - settings.PAGINATOR_LIMIT,
            'Incorrect number of posts on second page.'
        )

    def test_post_creation(self):
        """After post creation it is available on all relevant pages."""
        # Prepare test data
        Post.objects.create(
            author=PostsPageTests.author,
            text='New post',
            group=PostsPageTests.group
        )
        new_post = Post.objects.all()[0]
        urls_list = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPageTests.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': PostsPageTests.author.username})
        ]
        # Run test
        for url in urls_list:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.context['page_obj'][0],
                    new_post,
                    f'New post not in {repr(url)}'
                )
        self.assertEqual(
            new_post.pub_date.date(),
            datetime.date.today(),
            "Incorrect date in 'pub_date' field."
        )

    def test_group_page_has_only_group_posts(self):
        """Only group posts appear in group page."""
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPageTests.other_group.slug}
            )
        )
        self.assertIn(
            PostsPageTests.other_group_post,
            response.context['page_obj'],
            'Post not in its group page'
        )
        self.assertNotIn(
            PostsPageTests.posts,
            response.context['page_obj'],
            'Group page has other group posts'
        )

    @tag('slow')
    def test_index_page_caching(self):
        """Cached index page."""
        # Prepare test data
        url = reverse('posts:index')
        first_response = self.author_client.get(url)
        second_response = self.author_client.get(url)
        time.sleep(settings.CACHE_TIMEOUT)
        third_response = self.author_client.get(url)
        # Run test
        self.assertIsNotNone(
            first_response.context,
            'Context in not cached page is None'
        )
        self.assertIsNone(
            second_response.context,
            (f'Context within {settings.CACHE_TIMEOUT} seconds of cache '
             'timeout is not None')
        )
        self.assertIsNotNone(
            third_response.context,
            (f'Context after {settings.CACHE_TIMEOUT} seconds of cache '
             'timeout is not None')
        )

    def test_follow_index_context(self):
        """Only posts of following authors appear on follower page."""
        # Prepare test data
        url = reverse('posts:follow_index')
        new_post = Post.objects.create(
            author=PostsPageTests.other_author,
            text='New post'
        )
        follower_response = self.other_author_follower_client.get(url)
        not_follower_response = self.author_follower_client.get(url)
        # Run test
        self.assertEqual(
            follower_response.context['page_obj'][0],
            new_post,
            'New post does not appear on follower page'
        )
        self.assertNotEqual(
            not_follower_response.context['page_obj'][0],
            new_post,
            'New post appear on not follower page'
        )
        self.assertTrue(
            follower_response.context['follow'],
            f"Incorrect context['follow'] at {repr(url)}"
        )
        self.assertTrue(
            not_follower_response.context['follow'],
            f"Incorrect context['follow'] at {repr(url)}"
        )
