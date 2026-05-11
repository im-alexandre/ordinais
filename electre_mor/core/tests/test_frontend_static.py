from django.test import TestCase
from django.urls import reverse


class FrontendStaticTests(TestCase):
    def test_raiz_serva_shell_react_e_assets_estaticos(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "frontend_index.html")

        html = response.content.decode("utf-8", errors="ignore")
        self.assertIn('id="root"', html)
        self.assertIn("ELECTRE-MOr", html)
        self.assertIn("Start your project!", html)
        self.assertIn("/static/favicon.svg", html)
        self.assertIn("/static/frontend/assets/index.js", html)
        self.assertIn("/static/frontend/assets/index.css", html)
