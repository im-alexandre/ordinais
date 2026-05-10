# Tasks: Modernizacao da aplicacao ordinais

**Input**: Design documents from `/specs/001-api-react-refactor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md
**Tests**: Obrigatorios pela especificacao; criar testes antes das implementacoes correspondentes.
**Organization**: Tarefas agrupadas por historia para permitir execucao independente e paralela por multiagentes.

## Phase 1: Setup e baseline obrigatorio

**Purpose**: Criar a linha de base por URLs antes de qualquer mudanca funcional.

- [X] T001 Criar pacote de testes em electre_mor/core/tests/__init__.py
- [X] T002 [P] Criar fixtures minimas de projeto, decisores, criterios e alternativas em electre_mor/core/tests/fixtures/baseline_project.json
- [X] T003 Criar testes exploratorios de GET das URLs existentes em electre_mor/core/tests/test_url_baseline.py
- [X] T004 Criar testes exploratorios de POST e redirecionamentos dos fluxos existentes em electre_mor/core/tests/test_url_flow_baseline.py
- [X] T005 Executar baseline inicial e registrar comportamento esperado em electre_mor/core/tests/fixtures/url_baseline_expected.json
- [X] T006 Criar registro de documentacao consultada para implementacao em specs/001-api-react-refactor/implementation-notes.md

---

## Phase 2: Fundacao compartilhada

**Purpose**: Modernizar a base tecnica depois que o baseline estiver versionado.

- [X] T007 Atualizar runtime Python para 3.13 em electre_mor/runtime.txt
- [X] T008 Atualizar dependencias para Django 5.2, DRF 3.17, psycopg 3, gunicorn e whitenoise em electre_mor/requirements.txt
- [X] T009 Remover dependencia django-pandas de electre_mor/requirements.txt
- [X] T010 Atualizar imagem e instalacao do container para Python 3.13 em electre_mor/Dockerfile
- [X] T011 Atualizar PostgreSQL para versao compativel com Django 5.2 preservando labels Traefik em docker-compose.yml
- [X] T012 Atualizar imports de traducao removidos/depreciados em electre_mor/core/forms.py
- [X] T013 Atualizar configuracoes Django 5.2, DRF, staticfiles e WhiteNoise em electre_mor/electre_mor_project/settings.py
- [X] T014 Atualizar roteamento raiz para separar rotas legadas, API e fallback frontend em electre_mor/electre_mor_project/urls.py
- [X] T015 Criar pacote de API em electre_mor/core/api/__init__.py
- [X] T016 Criar modulo de URLs da API em electre_mor/core/api/urls.py
- [X] T017 Criar utilitarios de substituicao do django-pandas em electre_mor/core/tabular.py
- [X] T018 Atualizar notas de documentacao para decisoes Django 5.2 e DRF em specs/001-api-react-refactor/implementation-notes.md
- [X] T019 Executar python manage.py check e registrar resultado em specs/001-api-react-refactor/implementation-notes.md

**Checkpoint**: A base modernizada carrega sem alterar ainda os contratos de negocio finais.

---

## Phase 3: User Story 1 - Preservar comportamento existente das rotas (Priority: P1)

**Goal**: Garantir que as URLs atuais tenham comportamento registrado e comparavel antes e depois da refatoracao.

**Independent Test**: `cd electre_mor; python manage.py test core.tests.test_url_baseline core.tests.test_url_flow_baseline`

### Tests for User Story 1

- [ ] T020 [P] [US1] Criar teste de compatibilidade para landing page e pagina de metodo em electre_mor/core/tests/test_legacy_public_routes.py
- [ ] T021 [P] [US1] Criar teste de compatibilidade para criacao e cadastro de projeto em electre_mor/core/tests/test_legacy_project_flow.py
- [ ] T022 [P] [US1] Criar teste de compatibilidade para avaliacao e resultado em electre_mor/core/tests/test_legacy_result_flow.py
- [ ] T023 [P] [US1] Criar teste de regressao para download de resultado em electre_mor/core/tests/test_legacy_download.py

### Implementation for User Story 1

- [ ] T024 [US1] Atualizar views legadas para Django 5.2 mantendo respostas baseline em electre_mor/core/views.py
- [ ] T025 [US1] Substituir usos de DataFrameManager nos modelos por manager nativo em electre_mor/core/models.py
- [ ] T026 [US1] Substituir to_dataframe e to_pivot_table por utilitarios nativos em electre_mor/core/method.py
- [ ] T027 [US1] Ajustar calculo Electre para entradas tabulares atualizadas em electre_mor/core/ElectreTri.py
- [ ] T028 [US1] Atualizar templates legados ainda cobertos pelo baseline em electre_mor/templates/
- [ ] T029 [US1] Executar suite US1 e atualizar equivalencias justificadas em electre_mor/core/tests/fixtures/url_baseline_expected.json

**Checkpoint**: US1 deve passar antes de qualquer agente integrar API ou frontend.

---

## Phase 4: User Story 3 - Expor funcionalidades para consumo estruturado (Priority: P3)

**Goal**: Disponibilizar contratos de dados estruturados para projetos, participantes, avaliacoes, parametros e resultado.

**Independent Test**: `cd electre_mor; python manage.py test core.tests.test_api_contracts`

### Tests for User Story 3

- [ ] T030 [P] [US3] Criar testes de contrato para /api/v1/projects/ em electre_mor/core/tests/test_api_projects.py
- [ ] T031 [P] [US3] Criar testes de contrato para /api/v1/projects/{projectId}/participants/ em electre_mor/core/tests/test_api_participants.py
- [ ] T032 [P] [US3] Criar testes de contrato para avaliacoes e parametros em electre_mor/core/tests/test_api_evaluations.py
- [ ] T033 [P] [US3] Criar testes de contrato para /api/v1/projects/{projectId}/result/ em electre_mor/core/tests/test_api_result.py

### Implementation for User Story 3

- [ ] T034 [P] [US3] Criar serializers de Projeto, Decisor, Criterio e Alternativa em electre_mor/core/api/serializers.py
- [ ] T035 [P] [US3] Criar serializers de avaliacoes, parametros e resultado em electre_mor/core/api/evaluation_serializers.py
- [ ] T036 [P] [US3] Criar servico de persistencia de projetos e participantes em electre_mor/core/services/project_service.py
- [ ] T037 [P] [US3] Criar servico de avaliacoes e parametros em electre_mor/core/services/evaluation_service.py
- [ ] T038 [P] [US3] Criar servico de calculo de resultado para API em electre_mor/core/services/result_service.py
- [ ] T039 [US3] Implementar ViewSets e actions DRF de projetos em electre_mor/core/api/views.py
- [ ] T040 [US3] Conectar routers DRF e endpoints planejados em electre_mor/core/api/urls.py
- [ ] T041 [US3] Incluir rotas /api/v1/ no roteador principal em electre_mor/electre_mor_project/urls.py
- [ ] T042 [US3] Atualizar contrato OpenAPI conforme implementacao real em specs/001-api-react-refactor/contracts/openapi.yaml
- [ ] T043 [US3] Executar testes de contrato da API em electre_mor/core/tests/test_api_contracts.py

**Checkpoint**: US3 entrega API consumivel independentemente do frontend.

---

## Phase 5: User Story 2 - Consumir funcionalidades por interface web moderna (Priority: P2)

**Goal**: Entregar interface React clara, tech e premium, consumindo a API e servida pelo Django.

**Independent Test**: `cd electre_mor/frontend; npm run test && npm run build`, depois `cd electre_mor; python manage.py test core.tests.test_frontend_static`

### Tests for User Story 2

- [ ] T044 [P] [US2] Criar teste Django para servir index estatico do frontend em electre_mor/core/tests/test_frontend_static.py
- [ ] T045 [P] [US2] Criar testes de componentes da landing page em electre_mor/frontend/src/App.test.tsx
- [ ] T046 [P] [US2] Criar testes de cliente API do frontend em electre_mor/frontend/src/services/api.test.ts
- [ ] T047 [P] [US2] Criar teste de fluxo principal de avaliacao no frontend em electre_mor/frontend/src/pages/EvaluationFlow.test.tsx

### Implementation for User Story 2

- [ ] T048 [US2] Inicializar projeto React com Vite e TypeScript em electre_mor/frontend/package.json
- [ ] T049 [P] [US2] Configurar Vite para build estatico consumido pelo Django em electre_mor/frontend/vite.config.ts
- [ ] T050 [P] [US2] Criar cliente HTTP para endpoints /api/v1 em electre_mor/frontend/src/services/api.ts
- [ ] T051 [P] [US2] Criar tokens visuais claros e premium em electre_mor/frontend/src/styles/theme.css
- [ ] T052 [P] [US2] Criar componentes base de formulario e feedback em electre_mor/frontend/src/components/
- [ ] T053 [US2] Criar landing page com nome do metodo e acronimo em destaque em electre_mor/frontend/src/pages/LandingPage.tsx
- [ ] T054 [US2] Criar fluxo de criacao de projeto e participantes em electre_mor/frontend/src/pages/ProjectSetup.tsx
- [ ] T055 [US2] Criar fluxo de avaliacoes numericas e pareadas em electre_mor/frontend/src/pages/EvaluationFlow.tsx
- [ ] T056 [US2] Criar visualizacao de resultado em electre_mor/frontend/src/pages/ResultView.tsx
- [ ] T057 [US2] Integrar rotas React e estados de validacao em electre_mor/frontend/src/App.tsx
- [ ] T058 [US2] Criar template Django que serve o build React em electre_mor/templates/frontend_index.html
- [ ] T059 [US2] Criar view Django de fallback para SPA em electre_mor/core/frontend_views.py
- [ ] T060 [US2] Copiar ou coletar build do frontend em electre_mor/static/frontend/

**Checkpoint**: US2 entrega a experiencia visual moderna consumindo a API.

---

## Phase 6: Polish e validacao cruzada

**Purpose**: Validar integracao completa, documentacao e deploy.

- [ ] T061 [P] Atualizar quickstart com comandos reais finais em specs/001-api-react-refactor/quickstart.md
- [ ] T062 [P] Atualizar README operacional do projeto em README.md
- [ ] T063 Executar suite Django completa e registrar resultado em specs/001-api-react-refactor/implementation-notes.md
- [ ] T064 Executar testes e build do frontend e registrar resultado em specs/001-api-react-refactor/implementation-notes.md
- [ ] T065 Executar docker compose build validando Coolify/Traefik em docker-compose.yml
- [ ] T066 Executar verificacao final de ausencia de django-pandas em electre_mor/requirements.txt
- [ ] T067 Executar smoke manual ou Playwright de desktop/mobile e registrar evidencia em specs/001-api-react-refactor/implementation-notes.md
- [ ] T068 Revisar tarefas concluidas e marcar pendencias finais em specs/001-api-react-refactor/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 bloqueia tudo: nenhuma alteracao funcional antes de T001-T005.
- Phase 2 depende do baseline inicial.
- Phase 3 depende da Phase 2 e entrega o MVP de preservacao de comportamento.
- Phase 4 pode iniciar depois da Phase 2, mas so deve integrar no branch principal depois do checkpoint da US1.
- Phase 5 pode iniciar depois da Phase 4 expor contratos suficientes da API.
- Phase 6 depende das historias selecionadas estarem completas.

### User Story Dependencies

- **US1 (P1)**: primeira entrega funcional; valida preservacao das URLs.
- **US3 (P3)**: depende da fundacao e idealmente integra depois da US1; pode ser desenvolvida em worktree paralelo apos contratos de teste.
- **US2 (P2)**: depende dos contratos da US3 para consumo real; componentes visuais podem iniciar em paralelo com mocks.

### Multiagent Parallel Strategy

- **Agente A - Baseline/legado**: T001-T006, T020-T029.
- **Agente B - Fundacao/deps/infra**: T007-T019, T061-T066.
- **Agente C - API/contratos**: T030-T043.
- **Agente D - Frontend/UI**: T044-T060.
- **Agente E - Validacao/revisao**: T063-T068.

Usar fila de integracao: integrar primeiro Agente A, depois B, depois C, depois D, mantendo rebase ou cherry-pick dos worktrees restantes sobre a branch atualizada.

---

## Parallel Execution Examples

### Depois do baseline inicial

```text
Task: "Atualizar dependencias em electre_mor/requirements.txt"
Task: "Criar testes de compatibilidade em electre_mor/core/tests/test_legacy_public_routes.py"
Task: "Criar pacote API em electre_mor/core/api/__init__.py"
```

### User Story 3 em paralelo

```text
Task: "Criar serializers em electre_mor/core/api/serializers.py"
Task: "Criar servico de persistencia em electre_mor/core/services/project_service.py"
Task: "Criar servico de resultado em electre_mor/core/services/result_service.py"
Task: "Criar testes de contrato em electre_mor/core/tests/test_api_result.py"
```

### User Story 2 em paralelo

```text
Task: "Criar cliente API em electre_mor/frontend/src/services/api.ts"
Task: "Criar tema visual em electre_mor/frontend/src/styles/theme.css"
Task: "Criar testes de componentes em electre_mor/frontend/src/App.test.tsx"
Task: "Criar view fallback em electre_mor/core/frontend_views.py"
```

---

## Implementation Strategy

### MVP First

1. Concluir Phase 1 e versionar o baseline.
2. Concluir Phase 2 sem alterar expectativas do baseline.
3. Concluir Phase 3 e validar US1 com a mesma suite inicial.
4. Parar e demonstrar preservacao de comportamento.

### Incremental Delivery

1. Baseline e fundacao.
2. US1 preserva comportamento legado.
3. US3 adiciona API estruturada.
4. US2 troca a experiencia publica por React servido pelo Django.
5. Phase 6 fecha deploy, documentacao e evidencias.

### Integration Rules

- Testes de cada historia devem ser escritos antes da implementacao correspondente.
- Tarefas [P] podem rodar em paralelo quando editam arquivos diferentes.
- Tarefas sem [P] devem ser integradas em ordem.
- Commits automaticos do Spec Kit devem ser usados ao final de cada comando Speckit; worktrees paralelos devem ser integrados um por vez.
