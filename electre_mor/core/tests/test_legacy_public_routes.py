from django.test import TestCase
from django.urls import reverse


class LegacyPublicRoutesTests(TestCase):
    def test_landing_page_exibe_identidade_do_metodo(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ELECTRE-MOr")
        self.assertContains(response, "Start your project!")

    def test_pagina_do_metodo_exibe_nome_e_descritor(self):
        response = self.client.get(reverse("metodo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ELECTRE-MOr - Método")
        self.assertContains(response, "A multicriteria ordinal classification method.")
