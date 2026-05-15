# Multiplos Decisores Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar fluxo de multiplos decisores no ELECTRE-MOr com criador como primeiro decisor, convites por token, QR Code, avaliacao independente por decisor, agregacao igualitaria e deploy dev no Coolify.

**Architecture:** O backend Django/DRF passa a persistir avaliacoes no escopo do decisor e a expor APIs separadas para criador e decisor por token. O frontend React/Vite consome o contrato novo com fluxo simples para projeto individual, gestao de links para fluxo coletivo, QR Code responsivo e resultado manual. A execucao deve usar agentes especificos de `C:\Users\imale\.codex\agents` e revisao TDD apos cada bloco.

**Tech Stack:** Django, Django REST Framework, React, Vite, Vitest, React Testing Library, Selenium headless, Coolify API via Python `requests` com `env:COOLIFY_API_KEY`.

---

## Branch e agentes obrigatorios

Branch de implementacao: `feature/multiplos-decisores-dev`.

Agentes obrigatorios:

- Coordenacao: `tdd-implementation-coordinator`.
- Backend: `backend-django-drf-tdd`.
- Frontend: `frontend-react-vite-tdd`.
- Revisao por etapa: `tdd-quality-reviewer`.

Regras:

- Todo codigo de backend deve ser implementado por `backend-django-drf-tdd`.
- Todo codigo de frontend deve ser implementado por `frontend-react-vite-tdd`.
- Toda etapa implementada deve passar por `tdd-quality-reviewer` antes da proxima integracao.
- Agentes genericos so podem ser usados para exploracao ou tarefas sem edicao de codigo.
- Nao commitar `.superpowers/`, `.agents/skills/` ou `skills-lock.json` nesta feature, salvo pedido explicito.
- Usar containers para todos os testes e validacoes. Backend via `docker compose run --rm --entrypoint python electre_mor manage.py ...`; frontend via container `node:22-alpine`; E2E browser via Selenium/Chrome em container.

## Arquivos e responsabilidades

Backend:

- `electre_mor/core/models.py`: campos de coordenacao em `Decisor`, vinculo de decisor em notas numericas e estado de resultado gerado.
- `electre_mor/core/migrations/0007_multiplos_decisores.py`: migracao de schema para tokens, status, criador e notas por decisor.
- `electre_mor/core/services/project_service.py`: criacao do criador como primeiro decisor e gestao de convidados.
- `electre_mor/core/services/evaluation_service.py`: salvamento idempotente por `(projeto, decisor)`.
- `electre_mor/core/services/result_service.py`: completude, pendencias, trava de resultado e agregacao por media igualitaria.
- `electre_mor/core/api/serializers.py`: serializers de projeto, decisor, participantes e gestao de links.
- `electre_mor/core/api/evaluation_serializers.py`: serializers por token e resultado com pendencias.
- `electre_mor/core/api/views.py`: endpoints do criador, endpoints por token e geracao manual de resultado.
- `electre_mor/core/api/urls.py`: rotas adicionais se o viewset atual nao for suficiente.
- `electre_mor/core/tests/test_api_projects.py`: contrato de criador como primeiro decisor quando aplicavel.
- `electre_mor/core/tests/test_api_participants.py`: adicionar/listar/desativar decisores e links.
- `electre_mor/core/tests/test_api_evaluations.py`: token, idempotencia, completude e erros.
- `electre_mor/core/tests/test_api_result.py`: pendencias, geracao manual, trava e agregacao.
- `electre_mor/core/tests/test_browser_e2e_vaccine_case.py`: fluxo browser criador-convidado-resultado.
- `docker-compose.e2e.yml`: override local para Selenium/Chrome containerizado no gate E2E.

Frontend:

- `electre_mor/frontend/src/types.ts`: tipos de decisor, status, links, token, pendencias e resultado gerado.
- `electre_mor/frontend/src/services/api.ts`: cliente de APIs novas.
- `electre_mor/frontend/src/services/api.test.ts`: contratos do cliente.
- `electre_mor/frontend/src/App.tsx`: navegacao por `projectId`, `decisorToken` e views.
- `electre_mor/frontend/src/pages/ProjectSetup.tsx`: criador como primeiro decisor e saida para avaliacao/gestao.
- `electre_mor/frontend/src/pages/ProjectSetup.test.tsx`: fluxo individual e coletivo.
- `electre_mor/frontend/src/pages/EvaluationFlow.tsx`: avaliacao por decisor resolvido por estado ou token.
- `electre_mor/frontend/src/pages/EvaluationFlow.test.tsx`: salvar avaliacao por decisor/token.
- `electre_mor/frontend/src/pages/ResultView.tsx`: pendencias e geracao manual.
- `electre_mor/frontend/src/pages/ResultView.test.tsx`: pendencias, botao gerar e resultado.
- `electre_mor/frontend/src/components/QrShareCard.tsx`: QR Code responsivo.
- `electre_mor/frontend/src/components/QrShareCard.test.tsx`: renderizacao, copiar/baixar e layout mobile.
- `electre_mor/frontend/src/styles/theme.css`: layout de gestao de links e QR Code mobile.

Deploy:

- `deploy_coolify.md`: consultar apenas se necessario para nomes existentes.
- Skill `coolify-deploy`: usar API Coolify com `env:COOLIFY_API_KEY`, mesmo GitHub App, servidor e projeto, ambiente `desenvolvimento`, branch `feature/multiplos-decisores-dev`, dominio `electremor-dev.drg.ink`.

## Ordem de integracao

1. Backend schema e persistencia por decisor.
2. Backend APIs de decisores, token, completude e resultado manual.
3. Frontend API client.
4. Frontend setup/gestao e frontend avaliacao/resultado em paralelo apenas depois do cliente estabilizado.
5. E2E browser via container Selenium.
6. Revisao final.
7. Push da branch.
8. Deploy Coolify dev.

## Comandos containerizados padrao

Backend Django:

```powershell
docker compose build electre_mor
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests -v 2
docker compose run --rm --entrypoint python electre_mor manage.py check
```

Frontend React/Vite:

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test && npm run build"
```

E2E browser:

```powershell
docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build db_electre selenium
docker compose -f docker-compose.yml -f docker-compose.e2e.yml run --rm --entrypoint sh electre_mor -lc "SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub python manage.py test core.tests.test_browser_e2e_vaccine_case -v 2"
```

O E2E via browser e obrigatorio ao final. Se falhar, o agente responsavel deve corrigir e repetir o ciclo red-green-refactor ate o fluxo combinado passar em container.

## Task 1: Backend schema e persistencia por decisor

**Owner agent:** `backend-django-drf-tdd`

**Files:**

- Modify: `electre_mor/core/models.py`
- Create: `electre_mor/core/migrations/0007_multiplos_decisores.py`
- Modify: `electre_mor/core/services/project_service.py`
- Modify: `electre_mor/core/services/evaluation_service.py`
- Test: `electre_mor/core/tests/test_api_participants.py`
- Test: `electre_mor/core/tests/test_api_evaluations.py`

- [ ] **Step 1: Write failing backend tests for schema behavior**

Add tests that assert:

```python
def test_participantes_cria_primeiro_decisor_com_token_e_flag_criador(self):
    payload = {
        "decisores": [{"nome": "Criador"}],
        "criterios": [
            {"nome": "Qualidade", "numerico": False, "monotonico": 1},
            {"nome": "Custo", "numerico": True, "monotonico": 2},
        ],
        "alternativas": [{"nome": "A"}, {"nome": "B"}],
    }

    response = self.client.put(
        f"/api/v1/projects/{self.projeto.id}/participants/",
        payload,
        format="json",
    )

    self.assertEqual(response.status_code, 200)
    decisor = Decisor.objects.get(projeto=self.projeto, nome="Criador")
    self.assertTrue(decisor.is_criador)
    self.assertTrue(decisor.ativo)
    self.assertEqual(decisor.status, Decisor.Status.PENDENTE)
    self.assertGreaterEqual(len(decisor.token), 32)
```

```python
def test_notas_numericas_sao_independentes_por_decisor(self):
    decisor_1 = Decisor.objects.create(projeto=self.projeto, nome="D1")
    decisor_2 = Decisor.objects.create(projeto=self.projeto, nome="D2")

    substituir_notas_numericas(self.projeto, {
        "decisor": decisor_1,
        "scores": [{
            "criterio": self.criterio_1,
            "alternativa": self.alternativa_1,
            "nota": 8.0,
        }],
    })
    substituir_notas_numericas(self.projeto, {
        "decisor": decisor_2,
        "scores": [{
            "criterio": self.criterio_1,
            "alternativa": self.alternativa_1,
            "nota": 4.0,
        }],
    })

    notas = AlternativaCriterio.objects.filter(
        projeto=self.projeto,
        criterio=self.criterio_1,
        alternativa=self.alternativa_1,
    ).order_by("decisor__nome").values_list("decisor__nome", "nota")
    self.assertEqual(list(notas), [("D1", 8.0), ("D2", 4.0)])
```

- [ ] **Step 2: Run RED command**

Run:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_participants core.tests.test_api_evaluations -v 2
```

Expected: FAIL because `Decisor.token`, `Decisor.status`, `Decisor.is_criador`, `Decisor.ativo` or `AlternativaCriterio.decisor` do not exist yet.

- [ ] **Step 3: Implement minimal schema and service changes**

Implement:

- `Decisor.token` generated with a non-guessable token.
- `Decisor.status` with values `pendente`, `em_edicao`, `concluido`, `desativado`.
- `Decisor.ativo`.
- `Decisor.is_criador`.
- timestamps for created, completed and disabled states.
- `AlternativaCriterio.decisor`.
- deletion/replacement in `substituir_notas_numericas` scoped to `(projeto, decisor)`.
- creation of the first decisor as creator when participants are saved.

- [ ] **Step 4: Run GREEN command**

Run:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_participants core.tests.test_api_evaluations -v 2
```

Expected: PASS.

- [ ] **Step 5: Run migration and model validation**

Run:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py makemigrations --check --dry-run
docker compose run --rm --entrypoint python electre_mor manage.py check
```

Expected: no pending migrations beyond `0007_multiplos_decisores.py`; system check passes.

- [ ] **Step 6: Commit task**

```powershell
git add electre_mor/core/models.py electre_mor/core/migrations/0007_multiplos_decisores.py electre_mor/core/services/project_service.py electre_mor/core/services/evaluation_service.py electre_mor/core/tests/test_api_participants.py electre_mor/core/tests/test_api_evaluations.py
git commit -m "Add decision-maker scoped persistence"
```

## Task 2: Backend APIs de gestao de decisores e links

**Owner agent:** `backend-django-drf-tdd`

**Files:**

- Modify: `electre_mor/core/api/serializers.py`
- Modify: `electre_mor/core/api/views.py`
- Modify: `electre_mor/core/api/urls.py`
- Modify: `electre_mor/core/services/project_service.py`
- Test: `electre_mor/core/tests/test_api_participants.py`

- [ ] **Step 1: Write failing API tests**

Add tests that assert:

```python
def test_criador_adiciona_decisor_convidado_e_recebe_link(self):
    response = self.client.post(
        f"/api/v1/projects/{self.projeto.id}/decision-makers/",
        {"nome": "Ana Souza"},
        format="json",
    )

    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data["nome"], "Ana Souza")
    self.assertIn("token", response.data)
    self.assertIn("evaluation_url", response.data)
    self.assertIn("decisorToken=", response.data["evaluation_url"])
```

```python
def test_criador_desativa_decisor_pendente(self):
    decisor = Decisor.objects.create(projeto=self.projeto, nome="Ana Souza")

    response = self.client.post(
        f"/api/v1/projects/{self.projeto.id}/decision-makers/{decisor.id}/disable/",
        {},
        format="json",
    )

    self.assertEqual(response.status_code, 200)
    decisor.refresh_from_db()
    self.assertFalse(decisor.ativo)
    self.assertEqual(decisor.status, Decisor.Status.DESATIVADO)
```

- [ ] **Step 2: Run RED command**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_participants -v 2
```

Expected: FAIL with 404 for missing decision-maker endpoints.

- [ ] **Step 3: Implement minimal API**

Add creator endpoints to list, create and disable decision-makers. Preserve existing `/participants/` behavior for setup.

- [ ] **Step 4: Run GREEN and regression commands**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_participants core.tests.test_api_projects -v 2
```

Expected: PASS.

- [ ] **Step 5: Commit task**

```powershell
git add electre_mor/core/api/serializers.py electre_mor/core/api/views.py electre_mor/core/api/urls.py electre_mor/core/services/project_service.py electre_mor/core/tests/test_api_participants.py
git commit -m "Add decision-maker link management API"
```

## Task 3: Backend token evaluation, completude, resultado manual e agregacao

**Owner agent:** `backend-django-drf-tdd`

**Files:**

- Modify: `electre_mor/core/api/evaluation_serializers.py`
- Modify: `electre_mor/core/api/views.py`
- Modify: `electre_mor/core/api/urls.py`
- Modify: `electre_mor/core/services/evaluation_service.py`
- Modify: `electre_mor/core/services/result_service.py`
- Test: `electre_mor/core/tests/test_api_evaluations.py`
- Test: `electre_mor/core/tests/test_api_result.py`

- [ ] **Step 1: Write failing tests for token and errors**

Add tests for:

```python
def test_token_invalido_nao_resolve_avaliacao(self):
    response = self.client.get(
        f"/api/v1/projects/{self.projeto.id}/evaluation-token/invalido/"
    )

    self.assertIn(response.status_code, [403, 404])
```

```python
def test_decisor_desativado_retorna_410(self):
    decisor = Decisor.objects.create(
        projeto=self.projeto,
        nome="Ana",
        ativo=False,
        status=Decisor.Status.DESATIVADO,
    )

    response = self.client.get(
        f"/api/v1/projects/{self.projeto.id}/evaluation-token/{decisor.token}/"
    )

    self.assertEqual(response.status_code, 410)
```

```python
def test_resultado_retorna_pendencias_antes_da_geracao_manual(self):
    response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

    self.assertEqual(response.status_code, 409)
    self.assertIn("pendencias", response.data)
```

```python
def test_agrega_dois_decisores_ativos_com_peso_igual(self):
    resultado = obter_resultado_agregado(self.projeto)

    self.assertEqual(resultado["decisores_ativos"], 2)
    self.assertIn("classificacao_final", resultado)
```

- [ ] **Step 2: Run RED command**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_evaluations core.tests.test_api_result -v 2
```

Expected: FAIL because token endpoints, pendencias, manual generation or aggregation do not exist yet.

- [ ] **Step 3: Implement token and result services**

Implement:

- context endpoint by token;
- save-by-token or save-with-decisor flow;
- completion validation by decisor;
- `409` with pending decision-makers;
- manual generate action;
- lock after result generation;
- equal-weight aggregation before calling `ElectreTri`.

- [ ] **Step 4: Run GREEN command**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_evaluations core.tests.test_api_result -v 2
```

Expected: PASS.

- [ ] **Step 5: Run backend suite**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests -v 2
```

Expected: PASS.

- [ ] **Step 6: Commit task**

```powershell
git add electre_mor/core/api/evaluation_serializers.py electre_mor/core/api/views.py electre_mor/core/api/urls.py electre_mor/core/services/evaluation_service.py electre_mor/core/services/result_service.py electre_mor/core/tests/test_api_evaluations.py electre_mor/core/tests/test_api_result.py
git commit -m "Add token evaluation and manual result generation"
```

## Task 4: Frontend API client and types

**Owner agent:** `frontend-react-vite-tdd`

**Files:**

- Modify: `electre_mor/frontend/src/types.ts`
- Modify: `electre_mor/frontend/src/services/api.ts`
- Modify: `electre_mor/frontend/src/services/api.test.ts`

- [ ] **Step 1: Write failing client tests**

Add tests for:

```typescript
it('adiciona decisor convidado no projeto correto', async () => {
  fetchMock.mockResponseOnce(JSON.stringify({
    id: 9,
    nome: 'Ana Souza',
    status: 'pendente',
    ativo: true,
    token: 'token-seguro',
    evaluation_url: 'http://localhost/?projectId=4&decisorToken=token-seguro&view=avaliacao',
  }));

  const resultado = await adicionarDecisor(4, { nome: 'Ana Souza' });

  expect(fetchMock).toHaveBeenCalledWith(
    '/api/v1/projects/4/decision-makers/',
    expect.objectContaining({ method: 'POST' }),
  );
  expect(resultado.evaluation_url).toContain('decisorToken=token-seguro');
});
```

```typescript
it('gera resultado manualmente', async () => {
  fetchMock.mockResponseOnce(JSON.stringify({ status: 'generated' }));

  await gerarResultado(4);

  expect(fetchMock).toHaveBeenCalledWith(
    '/api/v1/projects/4/generate-result/',
    expect.objectContaining({ method: 'POST' }),
  );
});
```

- [ ] **Step 2: Run RED command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/services/api.test.ts"
```

Expected: FAIL because new client functions and types do not exist.

- [ ] **Step 3: Implement minimal client and types**

Add explicit types for decision-maker status, link management, token context, pending result and generate-result response. Add API functions for the backend endpoints.

- [ ] **Step 4: Run GREEN command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/services/api.test.ts"
```

Expected: PASS.

- [ ] **Step 5: Commit task**

```powershell
git add electre_mor/frontend/src/types.ts electre_mor/frontend/src/services/api.ts electre_mor/frontend/src/services/api.test.ts
git commit -m "Add multi-decision-maker frontend API client"
```

## Task 5: Frontend project setup and link management

**Owner agent:** `frontend-react-vite-tdd`

**Files:**

- Modify: `electre_mor/frontend/src/App.tsx`
- Modify: `electre_mor/frontend/src/pages/ProjectSetup.tsx`
- Modify: `electre_mor/frontend/src/pages/LandingPage.tsx`
- Create: `electre_mor/frontend/src/pages/ProjectSetup.test.tsx`
- Modify: `electre_mor/frontend/src/App.test.tsx`
- Modify: `electre_mor/frontend/src/styles/theme.css`

- [ ] **Step 1: Write failing setup tests**

Add tests for:

```typescript
it('permite criar projeto com criador como primeiro decisor e continuar para avaliacao', async () => {
  render(<ProjectSetup onProjetoCriado={onProjetoCriado} />);

  await user.type(screen.getByLabelText(/nome do projeto/i), 'Vacinas MOR');
  await user.type(screen.getByLabelText(/descricao/i), 'Analise coletiva');
  await user.type(screen.getByLabelText(/nome do criador/i), 'Alexandre');
  await user.type(screen.getByLabelText(/quantidade de classes/i), '3');
  await user.type(screen.getByLabelText(/quantidade de criterios/i), '2');
  await user.type(screen.getByLabelText(/quantidade de alternativas/i), '2');
  await user.type(screen.getByLabelText(/lambda/i), '0.65');

  await user.click(screen.getByRole('button', { name: /continuar para minha avaliacao/i }));

  expect(onProjetoCriado).toHaveBeenCalled();
});
```

```typescript
it('mostra acao para continuar avaliacao depois de adicionar convidados', async () => {
  render(<ProjectSetup onProjetoCriado={onProjetoCriado} />);

  expect(await screen.findByRole('button', { name: /adicionar decisor/i })).toBeEnabled();
  expect(await screen.findByRole('button', { name: /continuar para minha avaliacao/i })).toBeEnabled();
});
```

- [ ] **Step 2: Run RED command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/pages/ProjectSetup.test.tsx src/App.test.tsx"
```

Expected: FAIL because creator-name and link-management UI do not exist.

- [ ] **Step 3: Implement setup and link management UI**

Add creator name field, actions for individual/collective flow, guest list, copy link, disable pending and continue-to-evaluation action after invites.

- [ ] **Step 4: Run GREEN command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/pages/ProjectSetup.test.tsx src/App.test.tsx"
```

Expected: PASS.

- [ ] **Step 5: Commit task**

```powershell
git add electre_mor/frontend/src/App.tsx electre_mor/frontend/src/pages/ProjectSetup.tsx electre_mor/frontend/src/pages/LandingPage.tsx electre_mor/frontend/src/pages/ProjectSetup.test.tsx electre_mor/frontend/src/App.test.tsx electre_mor/frontend/src/styles/theme.css
git commit -m "Add project creator and link management flow"
```

## Task 6: Frontend token evaluation, result pending state and QR Code

**Owner agent:** `frontend-react-vite-tdd`

**Files:**

- Modify: `electre_mor/frontend/src/pages/EvaluationFlow.tsx`
- Modify: `electre_mor/frontend/src/pages/ResultView.tsx`
- Create: `electre_mor/frontend/src/components/QrShareCard.tsx`
- Create: `electre_mor/frontend/src/components/QrShareCard.test.tsx`
- Modify: `electre_mor/frontend/src/pages/EvaluationFlow.test.tsx`
- Create: `electre_mor/frontend/src/pages/ResultView.test.tsx`
- Modify: `electre_mor/frontend/src/styles/theme.css`

- [ ] **Step 1: Write failing UI tests**

Add tests for:

```typescript
it('avalia por token sem mostrar controles de estrutura', async () => {
  render(<EvaluationFlow projectId={4} decisorToken="token-seguro" />);

  expect(await screen.findByText(/fluxo de avaliacao/i)).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /configurar projeto/i })).not.toBeInTheDocument();
});
```

```typescript
it('mostra pendencias e habilita gerar resultado manualmente', async () => {
  render(<ResultView projectId={4} isCreator />);

  expect(await screen.findByText(/decisores pendentes/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /gerar resultado/i })).toBeDisabled();
});
```

```typescript
it('renderiza qr code mobile com imagem antes do texto', () => {
  render(<QrShareCard nome="Ana Souza" url="https://example.test/link" />);

  const qr = screen.getByLabelText(/qr code/i);
  const titulo = screen.getByText(/link de avaliacao de ana souza/i);
  expect(qr.compareDocumentPosition(titulo) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});
```

- [ ] **Step 2: Run RED command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/pages/EvaluationFlow.test.tsx src/pages/ResultView.test.tsx src/components/QrShareCard.test.tsx"
```

Expected: FAIL because QR component, token mode and manual result UI do not exist.

- [ ] **Step 3: Implement evaluation/result/QR UI**

Implement token-aware evaluation, pending result state, manual generate action and responsive QR card. QR Code should be generated client-side from the existing evaluation URL; do not create another backend token.

- [ ] **Step 4: Run GREEN command**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test -- src/pages/EvaluationFlow.test.tsx src/pages/ResultView.test.tsx src/components/QrShareCard.test.tsx"
```

Expected: PASS.

- [ ] **Step 5: Run frontend full validation**

```powershell
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test && npm run build"
```

Expected: PASS.

- [ ] **Step 6: Commit task**

```powershell
git add electre_mor/frontend/src/pages/EvaluationFlow.tsx electre_mor/frontend/src/pages/ResultView.tsx electre_mor/frontend/src/components/QrShareCard.tsx electre_mor/frontend/src/components/QrShareCard.test.tsx electre_mor/frontend/src/pages/EvaluationFlow.test.tsx electre_mor/frontend/src/pages/ResultView.test.tsx electre_mor/frontend/src/styles/theme.css
git commit -m "Add token evaluation result gating and QR sharing"
```

## Task 7: Browser E2E integration

**Owner agent:** `backend-django-drf-tdd`

**Files:**

- Modify: `electre_mor/core/tests/test_browser_e2e_vaccine_case.py`
- Create: `docker-compose.e2e.yml`
- Optional modify if static build changes are needed: `electre_mor/static/frontend/assets/index.js`
- Optional modify if static build changes are needed: `electre_mor/static/frontend/assets/index.css`

- [ ] **Step 1: Write failing E2E test**

Extend the Selenium headless test to:

```python
def test_criador_convida_decisor_e_gera_resultado_manual(self):
    self.abrir_aplicacao()
    self.criar_projeto_com_criador("Vacinas MOR", "Coordenador")
    link_convidado = self.adicionar_decisor_e_copiar_link("Ana Souza")
    self.preencher_avaliacao_do_criador()
    self.abrir_url(link_convidado)
    self.preencher_avaliacao_do_convidado()
    self.abrir_resultado_do_projeto()
    self.clicar_botao("Gerar resultado")
    self.aguardar_texto("Classificacao range")
    self.aguardar_texto("Classificacao quantile")
```

- [ ] **Step 2: Run RED command**

```powershell
docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build db_electre selenium
docker compose -f docker-compose.yml -f docker-compose.e2e.yml run --rm --entrypoint sh electre_mor -lc "SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub python manage.py test core.tests.test_browser_e2e_vaccine_case -v 2"
```

Expected: FAIL until backend and frontend paths are integrated.

- [ ] **Step 3: Implement smallest E2E support fixes**

Fix only integration gaps needed by the browser flow. Do not add new product behavior outside the approved spec. The Selenium test must support `SELENIUM_REMOTE_URL` and use remote Chrome when that variable is set. `docker-compose.e2e.yml` must add a `selenium` service based on `selenium/standalone-chrome` and must not be used by Coolify production deploy.

- [ ] **Step 4: Run GREEN and full validation**

```powershell
docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build db_electre selenium
docker compose -f docker-compose.yml -f docker-compose.e2e.yml run --rm --entrypoint sh electre_mor -lc "SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub python manage.py test core.tests.test_browser_e2e_vaccine_case -v 2"
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests -v 2
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test && npm run build"
```

Expected: PASS.

- [ ] **Step 5: Commit task**

```powershell
git add docker-compose.e2e.yml electre_mor/core/tests/test_browser_e2e_vaccine_case.py electre_mor/static/frontend/assets/index.js electre_mor/static/frontend/assets/index.css
git commit -m "Validate multi-decision-maker browser flow"
```

## Task 8: Quality review and final cleanup

**Owner agent:** `tdd-quality-reviewer`

**Files:**

- Read-only review across backend and frontend files changed by Tasks 1-7.

- [ ] **Step 1: Run reviewer**

Ask `tdd-quality-reviewer` to review:

- TDD evidence for every task;
- Django/DRF status codes, serializers, transactions, migrations and query scope;
- React Testing Library coverage, accessibility names, loading/error/empty states;
- no accidental commits of `.superpowers/`, `.agents/skills/` or `skills-lock.json`;
- QR Code mobile layout and token security risks.

- [ ] **Step 2: Fix any blocking findings with the appropriate implementation agent**

Backend fixes go to `backend-django-drf-tdd`; frontend fixes go to `frontend-react-vite-tdd`.

- [ ] **Step 3: Run final validation**

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests -v 2
docker run --rm -v "${PWD}\electre_mor\frontend:/app" -v electre_mor_frontend_node_modules:/app/node_modules -w /app node:22-alpine sh -lc "npm ci && npm test && npm run build"
docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build db_electre selenium
docker compose -f docker-compose.yml -f docker-compose.e2e.yml run --rm --entrypoint sh electre_mor -lc "SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub python manage.py test core.tests.test_browser_e2e_vaccine_case -v 2"
git status --short
```

Expected: backend PASS, frontend PASS, build PASS, E2E browser PASS, working tree clean except intentionally untracked local skill/cache artifacts.

## Task 9: Push and deploy Coolify desenvolvimento

**Owner:** main thread with `coolify-deploy` skill

**Files:**

- No source file edits expected.

- [ ] **Step 1: Push branch**

```powershell
git push -u origin feature/multiplos-decisores-dev
```

Expected: branch exists on `origin`.

- [ ] **Step 2: Load Coolify deployment context**

Use `env:COOLIFY_API_KEY`. Reuse the existing Coolify project, server and GitHub App for `ordinais`. Create or reuse a Coolify environment named `desenvolvimento`.

- [ ] **Step 3: Create or update dev application**

Set:

- branch: `feature/multiplos-decisores-dev`;
- domain: `electremor-dev.drg.ink`;
- GitHub App: same existing GitHub App used by the production/staging app;
- server: same existing server;
- project: same existing project;
- environment: `desenvolvimento`.

- [ ] **Step 4: Trigger deploy and validate**

Use Coolify API through Python `requests` wrappers from `coolify-deploy`. Validate public URL:

```powershell
Invoke-WebRequest -Uri "https://electremor-dev.drg.ink" -UseBasicParsing
```

Expected: HTTP 200 or valid application response from the deployed branch.

## Review checklist before execution completes

- [ ] Spec requirement "criador pode seguir sozinho" implemented and tested.
- [ ] Spec requirement "apos adicionar convidados, criador pode ir direto para avaliacao" implemented and tested.
- [ ] Tokens unique and non-guessable.
- [ ] Decisor invited cannot edit project structure.
- [ ] Evaluations saved by one decisor do not overwrite another.
- [ ] Pending/incomplete active decisors block manual result generation.
- [ ] Disabled decisors do not block result and do not enter aggregation.
- [ ] QR Code is generated from existing link and responsive mobile layout puts image above text.
- [ ] Result generation is manual and locks used evaluations.
- [ ] Coolify dev deploy uses `electremor-dev.drg.ink` and environment `desenvolvimento`.
