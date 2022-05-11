from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_template_map = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        """Test URL-addresses."""
        # Prepare error message
        error_msg = 'Wrong response status code for about url {}'
        # Run test
        for url in AboutURLTests.url_template_map:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    error_msg.format(repr(url))
                )

    def test_urls_use_correct_template(self):
        """URL-address uses correct template."""
        # Prepare error message
        error_msg = 'Wrong template: {} for url: {}.\n'
        # Run test
        for url, template in AboutURLTests.url_template_map.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))
