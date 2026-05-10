# Implementation Notes: Modernizacao da aplicacao ordinais

## Documentacao consultada

- Django 5.2 translation utilities: https://docs.djangoproject.com/en/5.2/ref/utils/
  - Uso: substituicao de `ugettext_lazy` por `gettext_lazy` em `core/forms.py`.
- Django 5.2 settings: https://docs.djangoproject.com/en/5.2/ref/settings/
  - Uso: `DEFAULT_AUTO_FIELD`, `ALLOWED_HOSTS`, `INSTALLED_APPS`, `TEMPLATES`, `DATABASES` e `STORAGES`.
- Django 5.2 static files: https://docs.djangoproject.com/en/5.2/howto/static-files/
  - Uso: `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS` e `STORAGES` com WhiteNoise.
- Django REST framework home: https://www.django-rest-framework.org/
  - Uso: confirmar suporte a Django 5.2/Python 3.13 antes de adicionar `rest_framework`.
- Django REST framework release notes: https://www.django-rest-framework.org/community/release-notes/
  - Uso: confirmar a serie 3.17.x como base compatível.
- Django REST framework routers: https://www.django-rest-framework.org/api-guide/routers/
  - Uso: scaffolding inicial de `core.api.urls` com `DefaultRouter`.
- Django 5.2 QuerySet API reference: https://docs.djangoproject.com/en/5.2/ref/models/querysets/
  - Uso: substituir `to_dataframe()`/`to_pivot_table()` por `values()`/`pivot_table()` nativos.
- Django 5.2 making queries: https://docs.djangoproject.com/en/5.2/topics/db/queries/
  - Uso: confirmar comportamento de `QuerySet` lazy e composição ao remover `django-pandas`.

## Execucoes

- 2026-05-10: baseline inicial T005 executado com `.venv-baseline` e comando `python manage.py test core.tests.test_url_baseline core.tests.test_url_flow_baseline -v 2`.
  - Resultado: 6 testes executados, OK.
  - Observacao: Docker nao estava disponivel porque o daemon nao estava rodando; foi usado ambiente virtual local com Django 3.2.25 e dependencias suficientes para capturar comportamento legado.
  - Observacao: rotas de resultado com dados incompletos sao observadas com `raise_request_exception=False`, permitindo preservar status 500 legado enquanto a refatoracao nao define equivalencia melhor.
- 2026-05-10: Phase 2 T007-T018 implementadas com atualizacao de runtime, dependencias, container, settings, roteamento, pacote `core.api`, utilitarios `core.tabular` e anotacoes de documentacao.
- 2026-05-10: dependencias atualizadas com `python -m pip install -r requirements.txt`; ambiente local passou a ter Django 5.2.3 e DRF 3.17.1 instalados.
- 2026-05-10: T019 executado com `python manage.py check`; bloqueio residual em `core.models` por `ModuleNotFoundError: No module named 'django_pandas'`, que ainda sera removido em fase posterior.
- 2026-05-10: validacao sintatica dos arquivos alterados com `python -m py_compile electre_mor/electre_mor_project/settings.py electre_mor/electre_mor_project/urls.py electre_mor/core/forms.py electre_mor/core/api/__init__.py electre_mor/core/api/urls.py electre_mor/core/tabular.py`.
- 2026-05-10: T020-T028 implementadas para US1 com testes legados, views/modelos/matriz tabular e ajuste do `ElectreTri` para `pandas` 2.x (`ExcelWriter.close()`).
- 2026-05-10: `python manage.py check` executado com sucesso após a remocao de `django_pandas` e a migracao do import legado `ugettext_lazy`.
- 2026-05-10: `python manage.py test core.tests.test_url_baseline core.tests.test_url_flow_baseline core.tests.test_legacy_public_routes core.tests.test_legacy_project_flow core.tests.test_legacy_result_flow core.tests.test_legacy_download` executado com sucesso.
