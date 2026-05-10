# Implementation Notes: Modernizacao da aplicacao ordinais

## Documentacao consultada

- Django 5.2 testing tools: https://docs.djangoproject.com/en/5.2/topics/testing/tools/
  - Uso: baseline com `django.test.Client` para GET, POST, status code, conteudo e redirects.
- Django 5.2 settings: https://docs.djangoproject.com/en/5.2/ref/settings/
  - Uso: referencia inicial para revisao futura de settings.
- Django 5.2 static files: https://docs.djangoproject.com/en/5.2/howto/static-files/
  - Uso: referencia inicial para servir o build estatico do frontend.

## Execucoes

- 2026-05-10: baseline inicial T005 executado com `.venv-baseline` e comando `python manage.py test core.tests.test_url_baseline core.tests.test_url_flow_baseline -v 2`.
  - Resultado: 6 testes executados, OK.
  - Observacao: Docker nao estava disponivel porque o daemon nao estava rodando; foi usado ambiente virtual local com Django 3.2.25 e dependencias suficientes para capturar comportamento legado.
  - Observacao: rotas de resultado com dados incompletos sao observadas com `raise_request_exception=False`, permitindo preservar status 500 legado enquanto a refatoracao nao define equivalencia melhor.
