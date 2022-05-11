from django.test import Client, TestCase
from django.urls import reverse


class AboutPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reverse_template_map = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_pages_use_correct_templates(self):
        """Pages use correct template."""
        # Prepare error message
        error_msg = 'Wrong template: {} for page: {}.\n'
        # Run test
        for url, template in AboutPageTests.reverse_template_map.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    error_msg.format(repr(template), repr(url)))
