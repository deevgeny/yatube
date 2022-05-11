from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.other_author = User.objects.create_user(username='other_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста',
            group=cls.group
        )
        cls.anonymous_url_template_map = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.authorized_url_template_map = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cls.authorized_url_without_template_redirect_map = {
            f'/posts/{cls.post.id}/comment/': f'/posts/{cls.post.id}/',
            f'/profile/{cls.author.username}/follow/':
                f'/profile/{cls.author.username}/',
            f'/profile/{cls.author.username}/unfollow/':
                f'/profile/{cls.author.username}/',

        }
        cls.unexisting_url = '/unexisting_page/'

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.other_author_client = Client()
        self.author_client.force_login(PostsURLTests.author)
        self.other_author_client.force_login(PostsURLTests.other_author)

    def tearDown(self):
        super().tearDown()
        # Clear cache for views with @cache_page() decorator
        cache.clear()

    def test_urls_exist_at_desired_location_anonymous(self):
        """Anonymous users URL-addresses."""
        # Prepare error message
        error_msg = 'Wrong response status code for anonymous user at url {}'
        # Run test
        for url in PostsURLTests.anonymous_url_template_map:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    error_msg.format(repr(url))
                )

    def test_urls_exist_at_desired_location_authorized(self):
        """Authorized users URL-addresses."""
        # Prepare error message
        error_msg = 'Wrong response status code for authorized user at url {}'
        # Run test
        for url in PostsURLTests.authorized_url_template_map:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    error_msg.format(repr(url)))

    def test_url_that_does_not_exist(self):
        """404 status code for unexisting page."""
        # Prepare error message
        error_msg = 'Wrong response status code for unexisting page at url {}'
        # Run test
        for client in [self.guest_client, self.author_client]:
            with self.subTest(client=client):
                response = client.get(PostsURLTests.unexisting_url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND.value,
                    error_msg.format(repr(PostsURLTests.unexisting_url))
                )

    def test_urls_redirect_anonymous(self):
        """Redirect anonymous users to /auth/login/?next=(...)."""
        # Prepare test data
        all_authorized_urls_to_check = [
            *PostsURLTests.authorized_url_template_map,
            *PostsURLTests.authorized_url_without_template_redirect_map
        ]
        # Run test
        for url in all_authorized_urls_to_check:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_urls_use_correct_template(self):
        """URL-address uses correct HTML template."""
        # Prepare test data
        error_msg = 'Wrong template: {} for url: {}.\n'
        all_urls_templates = {
            **PostsURLTests.authorized_url_template_map,
            **PostsURLTests.anonymous_url_template_map
        }
        # Run test
        for url, template in all_urls_templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))

    def test_url_redirect_when_try_to_edit_other_author_post(self):
        """URL redirects to post detail page."""
        response = self.other_author_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        self.assertRedirects(response, f'/posts/{PostsURLTests.post.pk}/')

    def test_url_without_template_redirect_authorized(self):
        """URL without template redirects to url with template."""
        for url, redirects_to in \
            PostsURLTests.authorized_url_without_template_redirect_map.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertRedirects(response, redirects_to)
