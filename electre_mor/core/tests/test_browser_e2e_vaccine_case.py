from pathlib import Path
import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BrowserE2EVaccineCaseTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1200")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        chrome_path = Path(
            r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if chrome_path.exists():
            options.binary_location = str(chrome_path)
        try:
            cls.browser = webdriver.Chrome(options=options)
        except WebDriverException as exc:
            raise unittest.SkipTest(f"Selenium Chrome indisponivel: {exc}") from exc
        cls.wait = WebDriverWait(cls.browser, 20)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "browser"):
            cls.browser.quit()
        super().tearDownClass()

    def clicar_botao(self, nome):
        botao = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space()='{nome}']")))
        botao.click()

    def preencher(self, rotulo, valor):
        campo = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 f"//span[normalize-space()='{rotulo}']/following-sibling::input")))
        campo.clear()
        campo.send_keys(valor)

    def test_fluxo_completo_electre_mor_com_vacinas(self):
        self.browser.get(self.live_server_url + "/")

        self.clicar_botao("Configurar projeto")
        self.preencher("Nome do projeto", "Caso Vacinas")
        self.preencher("Descricao", "Escolha de caixas termicas para vacinas")
        self.clicar_botao("Salvar projeto completo")

        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space()='Fluxo de avaliacao']")))
        self.assertTrue(
            self.browser.find_element(By.XPATH,
                                      "//*[contains(., 'Avaliações dos Critérios')]"))
        self.assertTrue(
            self.browser.find_element(
                By.XPATH,
                "//*[contains(., 'Qualidade') and contains(., 'Custo')]"))
        self.assertTrue(
            self.browser.find_element(By.XPATH,
                                      "//*[contains(., 'Avaliações Numéricas')]"))
        self.assertTrue(
            self.browser.find_element(By.XPATH,
                                      "//*[contains(., 'Custo:')]"))
        self.assertTrue(
            self.browser.find_element(
                By.XPATH,
                "//*[contains(., 'Vacina A') and contains(., 'Vacina B')]"))

        self.clicar_botao("Salvar avaliacao completa")

        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space()='Resultado']")))
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(., 'Classificacao range')]")))

        for nome in ("Vacina A", "Vacina B", "Vacina C", "Vacina D",
                     "Vacina E"):
            self.assertTrue(
                self.browser.find_element(By.XPATH,
                                          f"//*[contains(., '{nome}')]"))

        itens_range = self.browser.find_elements(
            By.CSS_SELECTOR,
            "section[aria-label='Classificacao range'] li",
        )
        self.assertEqual(len(itens_range), 5)
