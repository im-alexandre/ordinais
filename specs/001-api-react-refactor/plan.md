# Implementation Plan: Modernizacao da aplicacao ordinais

**Branch**: `001-api-react-refactor` | **Date**: 2026-05-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-api-react-refactor/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Modernizar a aplicacao Electre MOR preservando o comportamento das rotas atuais por uma suite exploratoria inicial, migrando o backend para Django 5.2 LTS com Django REST Framework, removendo `django-pandas`, mantendo compatibilidade com Coolify/Traefik e entregando um frontend React claro, premium e servido pelo proprio Django em producao.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2 LTS; frontend em TypeScript com React e Vite  
**Primary Dependencies**: Django 5.2.x, Django REST Framework 3.17.x, psycopg 3.x, gunicorn, whitenoise, numpy/pandas/scipy/scikit-learn atualizados; React 19.x, Vite 7.x, lucide-react  
**Storage**: PostgreSQL 14+ em producao; SQLite permitido apenas para desenvolvimento/testes locais se o projeto ja suportar  
**Testing**: Django `TestCase`/`Client` para baseline de URLs e regressao, DRF `APITestCase`/`APIClient` para contratos, Vitest/React Testing Library para componentes, Playwright para smoke visual quando o frontend estiver implementado  
**Target Platform**: Container Linux servido por gunicorn atras de Traefik/Coolify  
**Project Type**: Aplicacao web com backend Django, API REST e frontend estatico servido pelo backend  
**Performance Goals**: Fluxos representativos respondem em ate 2 s em ambiente local; chamadas estruturadas de leitura/escrita simples respondem em ate 1 s; build frontend carregavel em ate 3 s em rede comum  
**Constraints**: Nenhuma modificacao funcional antes da suite baseline; consultar documentacao oficial Django 5.x/DRF antes de cada decisao de classe, override ou API; remover `django-pandas`; preservar labels Traefik e exposicao de porta no `docker-compose.yml`; Django deve servir o build frontend em producao  
**Scale/Scope**: Escopo concentrado no app `electre_mor`, suas rotas atuais, modelos de projeto/criterio/alternativa/avaliacao/resultado e uma SPA React para os fluxos publicos principais

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituicao do projeto ainda contem placeholders e nao define gates acionaveis. Gates aplicaveis para esta feature vem da propria especificacao:

- PASS: testes exploratorios de URL devem ser a primeira tarefa de implementacao.
- PASS: modernizacao deve consultar documentacao oficial Django 5.x e DRF antes de escolher classes, overrides ou APIs.
- PASS: remocao de `django-pandas` deve manter comportamento calculado e coberto por regressao.
- PASS: deploy deve manter compatibilidade Coolify/Traefik.
- PASS: frontend React deve ser servido pelo backend Django em producao.

## Project Structure

### Documentation (this feature)

```text
specs/001-api-react-refactor/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
electre_mor/
├── core/
│   ├── models.py
│   ├── method.py
│   ├── ElectreTri.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── test_url_baseline.py
│       ├── test_api_contracts.py
│       └── test_calculation_regression.py
├── electre_mor_project/
│   ├── settings.py
│   └── urls.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── static/
│   └── frontend/
├── templates/
│   └── frontend_index.html
├── Dockerfile
├── entrypoint_electre.sh
└── requirements.txt

docker-compose.yml
specs/001-api-react-refactor/
└── contracts/
    └── openapi.yaml
```

**Structure Decision**: Manter o projeto Django existente em `electre_mor/`, adicionar um pacote `core/api/` para contratos REST, mover novos testes para `electre_mor/core/tests/` e colocar o app React em `electre_mor/frontend/`, com build copiado/coletado para `electre_mor/static/frontend/` e servido por uma view/template Django.

## Phase 0: Research

Concluido em [research.md](./research.md). Todas as decisoes tecnicas foram resolvidas sem marcadores `NEEDS CLARIFICATION`.

## Phase 1: Design & Contracts

Concluido:

- [data-model.md](./data-model.md)
- [contracts/openapi.yaml](./contracts/openapi.yaml)
- [quickstart.md](./quickstart.md)
- [AGENTS.md](../../AGENTS.md) atualizado para referenciar este plano

## Post-Design Constitution Check

- PASS: artefatos preservam teste baseline como primeira etapa obrigatoria.
- PASS: contratos usam recursos padrao de Django REST Framework em vez de endpoints ad hoc.
- PASS: modelo de dados explicita substituicao de `django-pandas` por consultas ORM e estruturas tabulares nativas da camada de calculo.
- PASS: quickstart inclui verificacoes para Coolify/Traefik, build estatico e regressao de URLs.
- PASS: nao ha violacoes constitucionais adicionais, pois a constituicao do projeto ainda nao possui regras especificas ratificadas.

## Complexity Tracking

Nenhuma violacao constitucional identificada.
