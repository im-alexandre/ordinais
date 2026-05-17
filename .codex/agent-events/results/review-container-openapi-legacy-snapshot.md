# Revisão do diff

Status: não aprovado.

## Achados

1. `electre_mor/core/services/result_service.py:46-55` ainda não garante a persistência do snapshot quando `resultado_snapshot` está vazio e o cache já tem um valor. Nesse caso, a função retorna o payload do cache e deixa o banco sem o snapshot legado corrigido. O teste novo em `electre_mor/core/tests/test_api_result.py:318-333` cobre apenas o caminho com `cache.clear()`, então não pega essa regressão.

2. `docker-compose.yml:12-14` mudou o build context para a raiz, mas `.dockerignore:1-21` ainda não exclui `.venv-baseline/`. No checkout atual esse diretório pesa cerca de 331 MB, então o build da Coolify tende a carregar contexto desnecessário e mais lento do que o necessário.

## Observação

A correção do `specs/001-api-react-refactor/contracts/openapi.yaml` no image build faz sentido e o fluxo validado pelo comando informado cobre o caso feliz, mas os dois pontos acima ainda merecem ajuste antes de aprovar.
