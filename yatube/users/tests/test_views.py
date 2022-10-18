from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(UsersPageTests.author)

    def test_pages_use_correct_templates_anonymous(self):
        """Pages use correct template with anonymous user."""
        # Prepare test data
        error_msg = 'Wrong template: {} for page: {}.\n'
        anonymous_reverse_template_map = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        # Run test
        for url, template in anonymous_reverse_template_map.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))

    def test_pages_use_correct_templates_authorized(self):
        """Pages use correct template with authorized user."""
        # Prepare test data
        error_msg = 'Wrong template: {} for page: {}.\n'
        authorized_reverse_template_map = {
            reverse('users:password_change'): 'users/password_change.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
        }
        # Run test
        for url, template in authorized_reverse_template_map.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))
