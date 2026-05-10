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
- Django REST framework serializers: https://www.django-rest-framework.org/api-guide/serializers/
  - Uso: priorizar `ModelSerializer` e serializers declarativos para os recursos de projeto.
- Django REST framework viewsets: https://www.django-rest-framework.org/api-guide/viewsets/
  - Uso: expor CRUD de projeto e actions aninhadas com `ModelViewSet` e `@action`.
- Django REST framework release notes: https://www.django-rest-framework.org/community/release-notes/
  - Uso: confirmar a serie 3.17.x como base compatível.
- Django REST framework routers: https://www.django-rest-framework.org/api-guide/routers/
  - Uso: scaffolding inicial de `core.api.urls` com `DefaultRouter`.
- Django REST framework testing: https://www.django-rest-framework.org/api-guide/testing/
  - Uso: estruturar testes de contrato com `APITestCase` e `APIClient`.
- Django 5.2 QuerySet API reference: https://docs.djangoproject.com/en/5.2/ref/models/querysets/
  - Uso: substituir `to_dataframe()`/`to_pivot_table()` por `values()`/`pivot_table()` nativos.
- Django 5.2 making queries: https://docs.djangoproject.com/en/5.2/topics/db/queries/
  - Uso: confirmar comportamento de `QuerySet` lazy e composição ao remover `django-pandas`.
- React `createRoot`: https://react.dev/reference/react-dom/client/createRoot
  - Uso: inicializacao do app React em `frontend/src/main.tsx`.
- React TypeScript: https://react.dev/learn/typescript
  - Uso: tipagem de componentes, props e servicos do frontend.
- Vite guide: https://vite.dev/guide/
  - Uso: estrutura do projeto, scripts e ambiente de desenvolvimento.
- Vite build: https://vite.dev/guide/build
  - Uso: configuracao do build estatico em `frontend/vite.config.ts`.
- Vitest guide: https://vitest.dev/guide/
  - Uso: configuracao de ambiente `jsdom`, setup e mocks de testes.
- Django 5.2 static files: https://docs.djangoproject.com/en/5.2/howto/static-files/
  - Uso: template de fallback da SPA e resolucao de assets estaticos.

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
- 2026-05-10: US3 validada com `python manage.py test core.tests.test_api_projects core.tests.test_api_participants core.tests.test_api_evaluations core.tests.test_api_result core.tests.test_api_contracts`.
- 2026-05-10: US2 validada com `npm run test`, `npm run build`, `python manage.py test core.tests.test_frontend_static` e `python manage.py test`.
- 2026-05-10: Polish T061-T066 executado; `docker compose build` concluiu com sucesso e `electre_mor/requirements.txt` nao contem `django-pandas`.
- 2026-05-10: Smoke manual T067 executado com `runserver` em `http://127.0.0.1:8010/` apos `python manage.py migrate`; `GET /` retornou 200 e `GET /api/v1/projects/` retornou 200. A porta 8000 estava ocupada por outro servico local.
- 2026-05-10: T030-T043 implementadas para US3 com serializers, services, viewset DRF, routers, contrato OpenAPI e testes `core.tests.test_api_*`.
- 2026-05-10: validacao da API executada com sucesso via `python manage.py test core.tests.test_api_projects core.tests.test_api_participants core.tests.test_api_evaluations core.tests.test_api_result core.tests.test_api_contracts`.
- 2026-05-10: T044-T060 implementadas para US2 com frontend React/Vite, cliente API, layout premium, view Django de fallback e build coletado em `static/frontend/`.
- 2026-05-10: frontend validado com `npm install`, `npm run test` e `npm run build` em `electre_mor/frontend`.
- 2026-05-10: fallback Django validado com `python manage.py test core.tests.test_frontend_static`.
- 2026-05-10: revisao final T068 concluiu com `python manage.py test` (31 testes OK), `npm run test` (5 testes OK), `npm run build` OK, `docker compose build` OK e verificacao final sem `django-pandas`.
