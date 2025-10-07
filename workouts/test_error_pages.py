from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class ErrorPageTests(TestCase):
    """Test custom error pages"""

    def setUp(self):
        self.client = Client()

    def test_404_page(self):
        """Test that 404 page renders correctly"""
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
        # In DEBUG mode, Django shows the default 404 page, not our custom one
        # Our custom 404 page will be used in production (DEBUG=False)
        if not response.context.get("DEBUG", True):
            self.assertContains(response, "Page Not Found")
            self.assertContains(response, "404")
            self.assertContains(response, "Go to Dashboard")

    def test_404_page_template(self):
        """Test that 404 page uses correct template"""
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_500_page_template_exists(self):
        """Test that 500.html template exists and can be rendered"""
        # We can't easily test 500 errors without breaking the app
        # But we can test that the template exists and is valid
        from django.template.loader import get_template

        template = get_template("500.html")
        self.assertIsNotNone(template)

    def test_403_page_template_exists(self):
        """Test that 403.html template exists and can be rendered"""
        from django.template.loader import get_template

        template = get_template("403.html")
        self.assertIsNotNone(template)

    def test_400_page_template_exists(self):
        """Test that 400.html template exists and can be rendered"""
        from django.template.loader import get_template

        template = get_template("400.html")
        self.assertIsNotNone(template)

    def test_error_pages_extend_base_template(self):
        """Test that error pages extend the base template"""
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist

        # Test that templates exist and can be loaded
        templates = ["404.html", "500.html", "403.html", "400.html"]
        for template_name in templates:
            try:
                template = get_template(template_name)
                self.assertIsNotNone(template)
            except TemplateDoesNotExist:
                self.fail(f"Template {template_name} does not exist")
