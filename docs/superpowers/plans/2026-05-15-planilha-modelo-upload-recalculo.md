# Plano de implementação: planilha modelo, upload parcial e recálculo oficial

> **Spec aprovada:** `docs/superpowers/specs/2026-05-15-planilha-modelo-upload-recalculo-design.md`

> **Regra de execução:** usar agentes especializados para implementação. O fio
> principal coordena, integra, resolve conflitos e executa validações finais.
> Cada fatia de implementação deve seguir RED -> GREEN -> REFACTOR e reportar a
> falha RED observada antes da correção.

## Objetivo

Implementar o fluxo alternativo em que o criador configura o projeto, baixa uma
planilha XLSX personalizada, preenche desempenhos de critérios numéricos e
opcionalmente `q`, `p`, `v`, faz upload, revisa valores importados/calculados,
confirma a importação e segue para o fluxo normal de avaliação. Também permitir
que apenas o criador edite `lambda` e número de classes na aba de resultado,
recalculando o resultado oficial sem exigir nova avaliação.

## Branch

Branch recomendada para a implementação:

`feature/planilha-modelo-upload-recalculo`

Derivar da branch dev atual, `feature/multiplos-decisores-dev`, depois de
confirmar que ela contém a spec aprovada.

## Agentes obrigatórios

- Coordenação: fio principal.
- Backend: `backend-django-drf-tdd`.
- Frontend: `frontend-react-vite-tdd`.
- Revisão: `tdd-quality-reviewer`.

Regras:

- Código backend deve ser feito pelo agente backend.
- Código frontend deve ser feito pelo agente frontend.
- Revisões de qualidade devem ser feitas por `tdd-quality-reviewer`.
- Evitar edição concorrente do mesmo arquivo.
- Integrar em fila: backend base primeiro, frontend depois dos contratos, revisão
  final por último.
- Não commitar artefatos locais como `.superpowers/`, `.codex-monitor/`,
  `.agents/skills/`, `skills-lock.json`, vídeos, screenshots ou downloads.

## Ordem de integração

1. Backend: contratos, serviços de planilha e recálculo oficial.
2. Frontend: cliente API e tipos, depois UI de download/upload/revisão.
3. Frontend: painel de recálculo no resultado.
4. Revisão especializada.
5. Validação local.
6. Push.
7. Aguardar auto-deploy do Coolify.
8. E2E headless no domínio dev.

## Matriz de paralelismo

| ID | Owner | Pode rodar em paralelo | Arquivos principais | Depende de | Gate RED | Gate GREEN |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | `backend-django-drf-tdd` | Sim, antes de views | `core/services/spreadsheet_service.py`, `core/tests/test_api_spreadsheet.py` | Nenhuma | serviço/template inexistente | XLSX com abas e conteúdo correto |
| B2 | `backend-django-drf-tdd` | Sim com B1, sem tocar views | `core/services/spreadsheet_service.py`, `core/tests/test_api_spreadsheet.py` | Nenhuma | parser/preview inexistente | preview calcula `q/p/v` e não grava banco |
| B3 | `backend-django-drf-tdd` | Não | `core/api/views.py`, serializers, testes API | B1, B2 | endpoints 404 | template, preview e confirm passam |
| B4 | `backend-django-drf-tdd` | Parcial; cuidado com `views.py` | `result_service.py`, views, serializers, testes resultado | Nenhuma para serviço; B3 para integração em views | endpoint 404 | recálculo atualiza projeto e snapshot |
| F1 | `frontend-react-vite-tdd` | Não | `types.ts`, `api.ts`, `api.test.ts` | B3, B4 integrados | funções ausentes | cliente cobre blob, upload e recálculo |
| F2 | `frontend-react-vite-tdd` | Sim com F3 após F1 | `ProjectSetup.tsx`, teste, CSS | F1 | UI de planilha ausente | revisão e confirmação funcionam |
| F3 | `frontend-react-vite-tdd` | Sim com F2 após F1 | `ResultView.tsx`, teste, CSS | F1, B4 | painel ausente/indevido | só criador recalcula oficialmente |
| Q1 | `tdd-quality-reviewer` | Não | leitura ampla | B/F integrados | achados documentados | sem bloqueantes |
| E1 | fio principal ou reviewer | Não | roteiro E2E headless | Q1, deploy dev | fluxo falha no domínio | fluxo completo passa |

## Gates TDD por fatia

- RED: criar teste primeiro e registrar a falha esperada por comportamento
  ausente, não por erro de sintaxe.
- GREEN: implementar o mínimo para passar o teste da fatia.
- REFACTOR: limpar duplicação ou nomes frágeis mantendo testes verdes.
- Backend: antes de escolher classe/override DRF ou resposta de arquivo,
  consultar documentação oficial Django 5.x/DRF e registrar a decisão no relato
  do agente.
- Frontend: testes com React Testing Library devem preferir papel, nome
  acessível, label e texto visível; evitar acoplamento a detalhes internos.
- Integração: quando duas fatias tocarem `views.py`, integrar uma por vez.

## Tarefa 1: Backend - defaults de projeto e recálculo oficial

**Owner agent:** `backend-django-drf-tdd`

**Objetivo:** garantir `lambda=0.75` quando vazio e criar endpoint que atualiza
`lambda` e número de classes, preserva avaliações e recalcula o resultado
oficial.

**Arquivos prováveis:**

- `electre_mor/core/api/views.py`
- `electre_mor/core/api/serializers.py`
- `electre_mor/core/services/result_service.py`
- `electre_mor/core/services/project_service.py`
- `electre_mor/core/tests/test_api_projects.py`
- `electre_mor/core/tests/test_api_result.py`

### RED

- Testar criação/atualização de projeto com `lambda` vazio assumindo `0.75`.
- Testar `POST /api/v1/projects/{id}/recalculate-result/` com novo `lambda` e
  `qtde_classes`.
- Testar que o recálculo:
  - atualiza `projeto.lamb`;
  - atualiza `projeto.qtde_classes`;
  - preserva avaliações já gravadas;
  - substitui `resultado_snapshot`;
  - retorna resultado atualizado.
- Testar que convidado/não criador não pode recalcular.
- Testar validação de limites de `lambda` e classes.

Comando:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_projects core.tests.test_api_result -v 2
```

### GREEN

Implementar o mínimo para os testes passarem:

- serializer de payload de recálculo;
- action DRF `recalculate_result`;
- serviço transacional que atualiza projeto e snapshot oficial;
- default `0.75` para `lambda` vazio no fluxo de projeto;
- permissões/checagem de criador conforme o contrato atual do frontend.

### Done

- Testes de projeto/resultado passam.
- Não há regressão de resultado manual existente.

## Tarefa 2: Backend - geração da planilha modelo

**Owner agent:** `backend-django-drf-tdd`

**Objetivo:** gerar XLSX personalizado para o projeto configurado.

**Arquivos prováveis:**

- `electre_mor/core/api/views.py`
- `electre_mor/core/services/spreadsheet_service.py`
- `electre_mor/core/tests/test_api_spreadsheet.py`
- `electre_mor/requirements.txt` se for necessária dependência backend para XLSX

### RED

- Testar `GET /api/v1/projects/{id}/spreadsheet-template/`.
- Validar `Content-Type` e download `.xlsx`.
- Abrir workbook no teste e verificar abas:
  - `Instrucoes`;
  - `Criterios`;
  - `Alternativas`;
  - `Parametros`.
- Verificar que critérios numéricos aparecem como colunas em `Alternativas`.
- Verificar que critérios qualitativos aparecem só em `Criterios`.
- Verificar aviso explícito sobre cálculo automático de `q`, `p`, `v`.

Comando:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_spreadsheet -v 2
```

### GREEN

Implementar serviço de geração XLSX com API estruturada. Preferir biblioteca já
disponível no backend se existir; se precisar dependência nova, justificar e
manter escopo mínimo.

### Done

- Workbook gerado é legível.
- Modelo não inclui abas por decisor.
- Modelo não pede desempenho de critério qualitativo.

## Tarefa 3: Backend - preview e confirmação do upload

**Owner agent:** `backend-django-drf-tdd`

**Objetivo:** validar planilha, calcular `q`, `p`, `v` vazios e confirmar dados
somente após revisão.

**Arquivos prováveis:**

- `electre_mor/core/api/views.py`
- `electre_mor/core/api/serializers.py`
- `electre_mor/core/services/spreadsheet_service.py`
- `electre_mor/core/services/evaluation_service.py`
- `electre_mor/core/tests/test_api_spreadsheet.py`

### RED

- Testar `POST /spreadsheet-upload/preview/` sem gravar no banco.
- Testar cálculo automático:
  - `q = 20%`;
  - `p = 40%`;
  - `v = 90%` da maior diferença.
- Testar preenchimento parcial preservando valores informados.
- Testar erros bloqueantes:
  - aba obrigatória ausente;
  - alternativa desconhecida;
  - critério numérico ausente;
  - desempenho vazio;
  - número inválido.
- Testar avisos não bloqueantes:
  - parâmetros calculados automaticamente;
  - coluna extra ignorada;
  - critério qualitativo ignorado.
- Testar `POST /spreadsheet-upload/confirm/` gravando desempenhos numéricos e
  parâmetros revisados.

Comando:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests.test_api_spreadsheet -v 2
```

### GREEN

Implementar:

- parser de workbook;
- estrutura JSON de preview;
- cálculo automático de parâmetros vazios;
- confirmação transacional;
- proteção contra gravação no preview.

### Done

- Preview não altera banco.
- Confirm grava dados corretos.
- Fluxo normal de avaliação segue funcionando.

## Tarefa 4: Frontend - cliente API e tipos da planilha

**Owner agent:** `frontend-react-vite-tdd`

**Depende de:** contratos backend das tarefas 1 a 3.

**Arquivos prováveis:**

- `electre_mor/frontend/src/types.ts`
- `electre_mor/frontend/src/services/api.ts`
- `electre_mor/frontend/src/services/api.test.ts`

### RED

- Testar download do template por `projectId`.
- Testar upload preview com `FormData`.
- Testar confirmação com payload revisado.
- Testar recálculo oficial com `lambda` e `qtde_classes`.

Comando:

```powershell
cd electre_mor/frontend
npm test -- --run src/services/api.test.ts
```

### GREEN

Implementar funções e tipos:

- `baixarPlanilhaModelo(projetoId)`;
- `preverUploadPlanilha(projetoId, arquivo)`;
- `confirmarUploadPlanilha(projetoId, payload)`;
- `recalcularResultado(projetoId, payload)`.

### Done

- Testes do cliente passam.
- Tipos representam origem dos parâmetros: planilha, automático, editado.

## Tarefa 5: Frontend - download/upload e revisão da planilha

**Owner agent:** `frontend-react-vite-tdd`

**Arquivos prováveis:**

- `electre_mor/frontend/src/pages/ProjectSetup.tsx`
- `electre_mor/frontend/src/components/SpreadsheetReview.tsx`
- `electre_mor/frontend/src/pages/ProjectSetup.test.tsx`
- `electre_mor/frontend/src/styles/theme.css`

### RED

- Testar ação `Baixar planilha modelo` após projeto configurado.
- Testar upload exibindo revisão antes de confirmar.
- Testar que revisão mostra:
  - desempenhos importados;
  - `q`, `p`, `v` calculados automaticamente;
  - `q`, `p`, `v` informados na planilha;
  - erros bloqueantes.
- Testar edição de `q`, `p`, `v` na revisão.
- Testar confirmação chamando API de confirm.

Comando:

```powershell
cd electre_mor/frontend
npm test -- --run src/pages/ProjectSetup.test.tsx
```

### GREEN

Implementar UI sem substituir o fluxo atual:

- manter botão de continuar para avaliação;
- adicionar caminho alternativo de planilha;
- estados de processamento, revisão, erro e confirmação;
- tabelas responsivas para revisão.

### Done

- Usuário consegue usar o caminho da planilha ou seguir manualmente.
- Revisão é clara e bloqueia confirmação quando houver erros.

## Tarefa 6: Frontend - recálculo oficial no resultado

**Owner agent:** `frontend-react-vite-tdd`

**Arquivos prováveis:**

- `electre_mor/frontend/src/pages/ResultView.tsx`
- `electre_mor/frontend/src/pages/ResultView.test.tsx`
- `electre_mor/frontend/src/styles/theme.css`

### RED

- Testar que apenas `isCreator` vê painel de recálculo.
- Testar campos `lambda` e `número de classes`.
- Testar clique em `Recalcular resultado` chamando API.
- Testar que resultado retornado substitui o resultado mostrado.
- Testar que convidados não veem o painel.

Comando:

```powershell
cd electre_mor/frontend
npm test -- --run src/pages/ResultView.test.tsx
```

### GREEN

Implementar painel compacto no resultado:

- input de `lambda`;
- input de `qtde_classes`;
- botão de recálculo;
- loading/error;
- atualização do resultado oficial na tela.

### Done

- Download XLSX existente usa o resultado atualizado em memória.
- UI deixa claro que é recálculo oficial.

## Tarefa 7: Revisão especializada

**Owner agent:** `tdd-quality-reviewer`

### Escopo

Revisar:

- preview não grava dados;
- confirm grava somente depois da revisão;
- cálculo automático `20/40/90%`;
- critérios qualitativos não aparecem como desempenho;
- recálculo atualiza projeto e snapshot oficial;
- convidados não veem controles de recálculo;
- testes TDD backend/frontend;
- riscos de parser XLSX e validação.

### Done

- Sem achados bloqueantes.
- Achados não bloqueantes documentados ou corrigidos.

## Tarefa 8: Validação local

**Owner:** fio principal

Comandos mínimos:

```powershell
docker compose run --rm --entrypoint python electre_mor manage.py test core.tests -v 2
cd electre_mor/frontend
npm test
npm run build
```

Se o frontend build alterar assets estáticos, commitar:

- `electre_mor/static/frontend/assets/index.css`
- `electre_mor/static/frontend/assets/index.js`
- chunks adicionais gerados.

## Tarefa 9: Deploy dev e E2E headless

**Owner:** fio principal com skill `coolify-deploy`

Regras:

- Se o projeto/ambiente/app/domínio Coolify já estiver saudável, não disparar
  redeploy manual.
- Fazer push da branch alvo.
- Aguardar o auto-deploy pelo GitHub App.
- Validar domínio `https://electremor-dev.drg.ink/`.

E2E headless deve cobrir:

- configurar projeto;
- baixar planilha modelo;
- preencher ou usar fixture XLSX;
- fazer upload;
- revisar `q`, `p`, `v` automáticos;
- editar ao menos um parâmetro;
- confirmar;
- seguir fluxo normal de avaliação;
- gerar resultado;
- alterar `lambda` e número de classes;
- recalcular resultado oficial;
- baixar XLSX final e validar que reflete o resultado atual.

## Checklist final

- [ ] Spec aprovada referenciada no plano.
- [ ] Backend implementado com TDD.
- [ ] Frontend implementado com TDD.
- [ ] Revisão especializada concluída.
- [ ] Testes backend passam.
- [ ] Testes frontend passam.
- [ ] Build frontend passa.
- [ ] Assets estáticos commitados.
- [ ] Branch pushada.
- [ ] Coolify auto-deploy concluído.
- [ ] E2E headless no domínio dev passa.
