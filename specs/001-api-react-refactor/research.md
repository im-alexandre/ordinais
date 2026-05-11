# Research: Modernizacao da aplicacao ordinais

## Decisao: usar Django 5.2 LTS com Python 3.13

**Rationale**: Django 5.2 e uma versao LTS e a documentacao oficial informa suporte a Python 3.10, 3.11, 3.12, 3.13 e 3.14. Python 3.13 e uma escolha conservadora dentro da faixa suportada e evita depender de suporte mais novo em bibliotecas cientificas que podem estar em transicao.

**Alternativas consideradas**:

- Python 3.14: suportado por Django 5.2 a partir de 5.2.8, mas pode ter compatibilidade mais recente em bibliotecas numericas.
- Python 3.12: tambem suportado e estavel, mas menos alinhado ao objetivo de modernizacao.

**Fonte consultada**: https://docs.djangoproject.com/en/5.2/releases/5.2/

## Decisao: usar Django REST Framework 3.17.x e seus generics/viewsets

**Rationale**: A pagina oficial do DRF declara suporte a Django 5.2 e Python 3.13/3.14. O plano deve usar `APIView` apenas para acoes calculadas e os generics/viewsets quando houver CRUD claro, porque a documentacao indica que `GenericAPIView` e views concretas ja fornecem comportamento comum de listagem, criacao, leitura, atualizacao e remocao.

**Alternativas consideradas**:

- Views Django com `JsonResponse`: rejeitado para contratos principais porque duplicaria validacao, parsing e serializacao ja disponiveis no DRF.
- Somente `APIView`: permitido para calculos sem CRUD simples, mas nao deve ser padrao para recursos modelados.

**Fontes consultadas**:

- https://www.django-rest-framework.org/
- https://www.django-rest-framework.org/api-guide/generic-views/
- https://www.django-rest-framework.org/api-guide/viewsets/
- https://www.django-rest-framework.org/api-guide/routers/
- https://www.django-rest-framework.org/community/release-notes/

## Decisao: criar baseline com Django Test Client antes de refatorar

**Rationale**: A documentacao de testes do Django recomenda o test client para simular GET/POST em URLs, observar status, conteudo, contexto e cadeia de redirecionamentos. Isso atende diretamente ao requisito de chamadas as URLs antes de qualquer modificacao funcional.

**Alternativas consideradas**:

- Selenium/Playwright como baseline inicial: util para UI renderizada, mas mais lento e menos direto para preservar comportamento das views.
- Testar view functions com `RequestFactory`: rejeitado como baseline principal porque ignora roteamento e middleware.

**Fonte consultada**: https://docs.djangoproject.com/en/5.2/topics/testing/tools/

## Decisao: remover `django-pandas` mantendo pandas apenas como estrutura de calculo interna se necessario

**Rationale**: O acoplamento atual esta no `DataFrameManager` e em chamadas como `to_dataframe()`/`to_pivot_table()`. A substituicao deve usar `QuerySet.values()`, `values_list()`, `annotate()`, `order_by()` e montagem explicita de `DataFrame` apenas dentro dos servicos de calculo quando a matematica existente depender disso. Assim a dependencia removida e `django-pandas`, nao necessariamente toda biblioteca tabular usada por algoritmos.

**Alternativas consideradas**:

- Remover tambem pandas: possivel em etapa futura, mas aumentaria risco porque `method.py` e `ElectreTri.py` trabalham naturalmente com tabelas numericas.
- Manter `django-pandas`: rejeitado por requisito explicito.

## Decisao: servir SPA por Django com staticfiles/WhiteNoise e fallback controlado

**Rationale**: A documentacao de static files do Django orienta configurar `django.contrib.staticfiles`, `STATIC_URL` e coleta de assets. Em producao, a aplicacao deve continuar atras de Traefik/Coolify e pode servir os assets coletados com WhiteNoise/gunicorn, enquanto uma rota Django retorna o `index.html` do frontend para os caminhos publicos nao-API.

**Alternativas consideradas**:

- Servico Node separado: rejeitado porque o requisito pede que o proprio Django sirva a pagina estatica do build.
- Nginx dedicado: rejeitado para manter simplificacao atual e compatibilidade Coolify/Traefik sem reintroduzir servico extra.

**Fonte consultada**: https://docs.djangoproject.com/en/5.2/howto/static-files/

## Decisao: manter uma unica aplicacao container com Postgres atualizado

**Rationale**: O `docker-compose.yml` atual ja usa um servico Django e labels Traefik. Django 5.2 remove suporte a PostgreSQL 13; portanto o banco deve ser atualizado para PostgreSQL 14+ para manter compatibilidade oficial.

**Alternativas consideradas**:

- Manter PostgreSQL 12: rejeitado por incompatibilidade com o suporte oficial do Django 5.2.
- Separar frontend e backend em containers distintos: rejeitado pelo requisito de servir build estatico pelo Django.

**Fonte consultada**: https://docs.djangoproject.com/en/5.2/releases/5.2/
