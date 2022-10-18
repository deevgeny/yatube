from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='author', email='author@mail.com', password='pass'
        )
        cls.anonymous_url_template_map = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        cls.authorized_url_template_map = {
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(UsersURLTests.author)

    def test_urls_exist_at_desired_location_anonymous(self):
        """Anonymous users URL-addresses."""
        # Prepare error message
        error_msg = 'Wrong response status code for anonymous user at url {}'
        # Run test
        for url in UsersURLTests.anonymous_url_template_map:
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
        for url in UsersURLTests.authorized_url_template_map:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    error_msg.format(repr(url)))

    def test_urls_redirect_anonymous(self):
        """Redirect anonymous users."""
        for url in UsersURLTests.authorized_url_template_map:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_urls_uses_correct_template(self):
        """URL-address uses correct template."""
        # Prepare test data
        error_msg = 'Wrong template: {} for url: {}.\n'
        all_urls_templates = {
            **UsersURLTests.authorized_url_template_map,
            **UsersURLTests.anonymous_url_template_map
        }
        # Run test
        for url, template in all_urls_templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))
