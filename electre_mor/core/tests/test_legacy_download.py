from pathlib import Path
from zipfile import ZipFile

from django.test import TestCase
from django.urls import reverse

from core.models import Projeto


class LegacyDownloadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.projeto = Projeto.objects.create(
            id=1,
            nome="Download",
            descricao="Projeto para regressao de download",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.5,
        )

    def setUp(self):
        self.resultados_dir = Path("resultados")
        self.resultados_dir.mkdir(parents=True, exist_ok=True)
        self.zip_path = self.resultados_dir / f"result_{self.projeto.id}.zip"
        self.bh_path = self.resultados_dir / f"result_bh_{self.projeto.id}.xlsx"
        self.bn_path = self.resultados_dir / f"result_bn_{self.projeto.id}.xlsx"
        self._write_placeholder(self.bh_path)
        self._write_placeholder(self.bn_path)

    def tearDown(self):
        for path in (self.zip_path, self.bh_path, self.bn_path):
            if path.exists():
                path.unlink()

    @staticmethod
    def _write_placeholder(path):
        path.write_bytes(b"placeholder")

    def test_download_entrega_arquivo_zip_em_anexo(self):
        response = self.client.get(
            reverse("download_file", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename=result_{self.projeto.id}.zip",
        )
        self.assertTrue(self.zip_path.exists())
        with ZipFile(self.zip_path) as archive:
            self.assertEqual(
                sorted(archive.namelist()),
                [
                    f"result_bh_{self.projeto.id}.xlsx",
                    f"result_bn_{self.projeto.id}.xlsx",
                ],
            )
