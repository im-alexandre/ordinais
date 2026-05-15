# Planilha modelo, upload parcial e recálculo oficial

Data: 2026-05-15

## Contexto

O fluxo atual do ELECTRE-MOr permite configurar um projeto no frontend, cadastrar
critérios, alternativas e decisores, coletar avaliações pelo criador e pelos
decisores convidados, gerar manualmente o resultado e baixar a tabela final em
XLSX.

A nova funcionalidade não substitui esse fluxo. Ela adiciona uma rota alternativa
para acelerar o preenchimento dos dados numéricos do projeto por meio de uma
planilha modelo personalizada. O objetivo é reduzir o volume de preenchimento
manual no app sem mover as avaliações dos decisores para Excel.

## Objetivos

- Permitir que o criador configure a estrutura do projeto no app antes do
  download da planilha.
- Gerar uma planilha modelo personalizada para o projeto configurado.
- Permitir upload da planilha preenchida com desempenhos dos critérios
  numéricos.
- Permitir que `q`, `p` e `v` sejam informados na planilha, mas torná-los
  opcionais.
- Calcular automaticamente `q`, `p` e `v` vazios a partir da maior diferença de
  desempenho de cada critério numérico.
- Exibir uma tela de revisão antes de gravar os dados importados.
- Permitir editar `q`, `p` e `v` na revisão.
- Manter o fluxo normal de avaliação dos decisores após a confirmação do upload.
- Permitir que apenas o criador edite `lambda` e número de classes no resultado
  e recalcule o resultado oficial sem exigir nova avaliação.

## Fora de escopo

- Importar avaliações de decisores via planilha.
- Criar uma aba por decisor na planilha.
- Substituir links individuais de avaliação por Excel.
- Gerar resultado imediatamente após o upload da planilha, antes das avaliações
  necessárias do fluxo normal.
- Criar histórico versionado de simulações. O recálculo atualiza o resultado
  oficial.

## Fluxo do usuário

1. O criador entra em `Configurar projeto`.
2. O criador informa dados estruturais do projeto:
   - nome;
   - descrição;
   - quantidade de classes, ou deixa em branco quando a UI permitir default;
   - `lambda`, ou deixa em branco para usar `0.75`;
   - critérios;
   - tipo de cada critério, numérico ou qualitativo;
   - direção de cada critério, lucro ou custo;
   - alternativas;
   - decisores opcionais.
3. O criador salva a estrutura do projeto.
4. O sistema oferece a ação `Baixar planilha modelo`.
5. O criador preenche a planilha com os desempenhos dos critérios numéricos e,
   se quiser, `q`, `p` e `v`.
6. O criador faz upload da planilha.
7. O sistema valida a planilha e mostra a tela de revisão.
8. A revisão mostra:
   - desempenhos numéricos importados;
   - parâmetros `q`, `p`, `v` informados pelo usuário;
   - parâmetros calculados automaticamente;
   - campos editáveis para `q`, `p`, `v`;
   - erros bloqueantes;
   - avisos não bloqueantes.
9. O criador confirma a importação.
10. O sistema grava os desempenhos numéricos e parâmetros no projeto.
11. O criador segue para o fluxo normal de avaliação.
12. Após gerar o resultado, apenas o criador pode editar `lambda` e número de
    classes na aba de resultado e recalcular o resultado oficial.

## Contrato da planilha modelo

A planilha deve ser XLSX e personalizada a partir do projeto salvo.

### Aba `Instrucoes`

Conteúdo textual com regras de preenchimento:

- A planilha serve apenas para critérios numéricos.
- Critérios qualitativos continuam sendo avaliados no app.
- Campos `q`, `p` e `v` são opcionais.
- Se `q`, `p` ou `v` ficarem vazios, o sistema calculará automaticamente:
  - `q = 20%` da maior diferença de desempenho do critério;
  - `p = 40%` da maior diferença de desempenho do critério;
  - `v = 90%` da maior diferença de desempenho do critério.
- Não alterar nomes de abas, nomes de critérios ou nomes de alternativas.

### Aba `Criterios`

Aba de referência, preferencialmente protegida ou marcada como somente leitura
quando possível:

| criterio_id | nome | tipo | direcao | preenchimento |
| --- | --- | --- | --- | --- |
| 1 | Custo total | numerico | custo | preencher em Alternativas |
| 2 | Impacto social | qualitativo | lucro | avaliar no app |

Critérios qualitativos aparecem aqui apenas para orientar o usuário. Eles não
geram colunas de desempenho na aba `Alternativas`.

### Aba `Alternativas`

Aba de preenchimento dos desempenhos numéricos.

| alternativa_id | alternativa | Custo total | Prazo | Emissoes |
| --- | --- | --- | --- | --- |
| 1 | Solar | 100 | 12 | 30 |
| 2 | Eólica | 80 | 10 | 20 |

Regras:

- Cada linha representa uma alternativa do projeto.
- Cada coluna de desempenho representa um critério numérico.
- Todas as células de desempenho numérico são obrigatórias.
- O sistema deve usar identificadores internos quando presentes, e nomes como
  apoio de legibilidade.
- Critérios qualitativos não aparecem como colunas de desempenho.

### Aba `Parametros`

Aba para preenchimento opcional de `q`, `p`, `v` por critério numérico.

| criterio_id | criterio | q | p | v |
| --- | --- | --- | --- | --- |
| 1 | Custo total |  |  |  |
| 3 | Emissoes | 2 | 5 |  |

Regras:

- Células vazias são calculadas automaticamente no upload.
- Células preenchidas pelo usuário são preservadas.
- Preenchimento parcial é permitido.
- O sistema deve indicar na revisão se cada valor veio da planilha ou do cálculo
  automático.

## Cálculo automático de q, p, v

Para cada critério numérico:

1. Ler todos os desempenhos das alternativas.
2. Calcular `maior_diferenca = max(valor) - min(valor)`.
3. Para cada parâmetro vazio:
   - `q = maior_diferenca * 0.20`;
   - `p = maior_diferenca * 0.40`;
   - `v = maior_diferenca * 0.90`.

Regras adicionais:

- Se todos os desempenhos forem iguais, `maior_diferenca = 0` e os parâmetros
  automáticos ficam `0`.
- O sistema deve aceitar números com separador decimal compatível com entrada
  comum em planilhas, desde que consiga converter de forma inequívoca.
- O backend deve normalizar os valores para o formato numérico usado pelos
  modelos existentes.

## Lambda

`lambda` é atributo do projeto.

- Se o criador deixar `lambda` vazio na configuração, o sistema usa `0.75`.
- A planilha modelo não é responsável por editar `lambda`.
- Na aba `Resultado`, apenas o criador pode editar `lambda`.
- Ao recalcular, o sistema atualiza `projeto.lamb`, recalcula o resultado
  oficial e atualiza o snapshot oficial.
- O XLSX de resultado sempre reflete o `lambda` atualmente salvo no projeto.

## Número de classes

O número de classes também é atributo oficial do projeto.

- Na aba `Resultado`, apenas o criador pode editar o número de classes.
- Ao recalcular, o sistema atualiza `projeto.qtde_classes`, preserva todas as
  avaliações existentes e recalcula apenas o resultado oficial.
- Mudar o número de classes não exige nova avaliação.
- O backend deve validar limites mínimos e máximos coerentes com o método e com
  a estrutura atual do projeto.
- O XLSX de resultado sempre reflete o número de classes atualmente salvo no
  projeto.

## Tela de revisão do upload

A revisão aparece depois do upload e antes de qualquer gravação definitiva.

Estados esperados:

- `Processando planilha`
- `Revisão pronta`
- `Erro bloqueante`
- `Confirmando importação`
- `Importação confirmada`

Componentes esperados:

- Resumo do arquivo importado.
- Tabela de desempenhos numéricos por alternativa.
- Tabela de parâmetros `q`, `p`, `v` por critério.
- Indicador visual por célula de parâmetro:
  - informado na planilha;
  - calculado automaticamente;
  - editado na revisão.
- Lista de avisos.
- Lista de erros bloqueantes.
- Botões:
  - `Confirmar importação`;
  - `Cancelar`;
  - `Baixar novo modelo`, quando fizer sentido.

## Validação

Erros bloqueantes:

- Arquivo ausente ou formato diferente de XLSX.
- Aba obrigatória ausente.
- Critério numérico esperado ausente na aba `Alternativas`.
- Alternativa esperada ausente.
- Valor de desempenho numérico vazio.
- Valor de desempenho ou parâmetro inválido.
- Identificador de critério ou alternativa que não pertence ao projeto.
- Planilha de outro projeto, quando identificável.

Avisos não bloqueantes:

- `q`, `p` ou `v` calculado automaticamente.
- Critérios qualitativos ignorados na planilha.
- Colunas extras ignoradas.
- Nomes divergentes quando o identificador interno ainda permite mapear o dado.

## Persistência e APIs

O design deve favorecer endpoints explícitos no backend DRF:

- `GET /api/v1/projects/{id}/spreadsheet-template/`
  - retorna XLSX personalizado.
- `POST /api/v1/projects/{id}/spreadsheet-upload/preview/`
  - recebe XLSX;
  - valida;
  - calcula parâmetros automáticos;
  - retorna JSON de revisão sem gravar.
- `POST /api/v1/projects/{id}/spreadsheet-upload/confirm/`
  - recebe o payload revisado;
  - grava desempenhos numéricos e parâmetros;
  - retorna contexto atualizado do projeto.
- `POST /api/v1/projects/{id}/recalculate-result/`
  - permitido apenas ao criador;
  - recebe `lambda` e `qtde_classes`;
  - atualiza o projeto;
  - recalcula o resultado oficial;
  - atualiza o snapshot oficial;
  - retorna o resultado atualizado.

Os nomes finais dos endpoints podem ser ajustados durante implementação, mas a
separação entre preview sem gravação e confirmação com gravação é requisito do
produto.

## UI esperada

### Configuração do projeto

Após salvar a estrutura do projeto, o criador deve conseguir baixar a planilha
modelo personalizada. A ação não deve substituir a opção de continuar direto
para avaliação.

### Upload da planilha

O upload deve aparecer como caminho alternativo para preencher dados numéricos.
A interface deve deixar claro que o usuário pode continuar manualmente se
preferir.

### Resultado

A aba `Resultado` deve ter um painel visível apenas para o criador com:

- campo `lambda`;
- campo `número de classes`;
- botão `Recalcular resultado`.

O recálculo é oficial, não uma simulação temporária. Depois do recálculo, a tela
e o download XLSX usam o novo resultado.

## Estratégia com agentes especializados

A implementação deve ser fatiada para evitar conflitos e permitir trabalho em
paralelo. O coordenador deve manter uma fila de integração, trazendo um conjunto
de mudanças por vez para a branch principal da feature.

### Agente backend: planilha e APIs

Tipo recomendado: `backend-django-drf-tdd`.

Escopo:

- Gerar XLSX modelo personalizado.
- Implementar parser de upload.
- Implementar cálculo automático de `q`, `p`, `v`.
- Implementar endpoints de preview e confirmação.
- Implementar endpoint de recálculo oficial por `lambda` e número de classes.
- Cobrir com testes Django/DRF.

Arquivos prováveis:

- `electre_mor/core/api/views.py`
- `electre_mor/core/api/serializers.py`
- `electre_mor/core/api/evaluation_serializers.py`
- `electre_mor/core/services/`
- `electre_mor/core/tests/`

### Agente frontend: fluxo de planilha e resultado

Tipo recomendado: `frontend-react-vite-tdd`.

Escopo:

- Adicionar ações de download/upload da planilha no fluxo de configuração.
- Criar tela ou painel de revisão do upload.
- Mostrar origem dos `q`, `p`, `v`.
- Permitir edição de `q`, `p`, `v` na revisão.
- Adicionar painel de recálculo no resultado apenas para criador.
- Atualizar cliente API e testes React Testing Library.

Arquivos prováveis:

- `electre_mor/frontend/src/pages/ProjectSetup.tsx`
- `electre_mor/frontend/src/pages/ResultView.tsx`
- `electre_mor/frontend/src/services/api.ts`
- `electre_mor/frontend/src/types.ts`
- `electre_mor/frontend/src/styles/theme.css`
- testes em `electre_mor/frontend/src/**/*.test.tsx`

### Agente de qualidade

Tipo recomendado: `tdd-quality-reviewer`.

Escopo:

- Revisar aderência ao fluxo combinado.
- Verificar cobertura TDD.
- Verificar se upload preview não grava dados antes da confirmação.
- Verificar se recálculo atualiza projeto e snapshot oficial.
- Verificar se convidados não veem controles exclusivos do criador.

### Coordenação e integração

O coordenador deve:

1. Criar branch de implementação a partir da branch dev atual.
2. Lançar agentes com escopos de escrita separados.
3. Integrar primeiro o backend, porque define contratos.
4. Rebasear ou ajustar frontend contra contratos finais.
5. Rodar testes backend, frontend e build.
6. Fazer E2E headless no domínio de desenvolvimento após push e auto-deploy do
   Coolify.
7. Não disparar redeploy manual se o ambiente Coolify já estiver saudável; fazer
   push e monitorar o deploy automático do GitHub App.

## Critérios de aceite

- Criador consegue baixar uma planilha modelo personalizada de um projeto
  configurado.
- Planilha mostra critérios qualitativos como referência, sem campos de
  desempenho.
- Planilha permite preencher desempenhos de critérios numéricos.
- Planilha permite preencher `q`, `p`, `v`, mas informa que são opcionais.
- Upload com `q`, `p`, `v` vazios calcula valores automaticamente.
- Upload parcial preserva valores informados e calcula apenas vazios.
- Revisão mostra origem dos parâmetros e permite edição antes de confirmar.
- Confirmação grava dados no projeto.
- Fluxo normal de avaliação dos decisores continua funcionando.
- `lambda` vazio assume `0.75`.
- Apenas criador vê painel de recálculo no resultado.
- Criador pode alterar `lambda` e número de classes no resultado.
- Recálculo preserva avaliações, atualiza projeto, recalcula resultado oficial e
  atualiza snapshot.
- Download XLSX reflete o resultado oficial atual.
- E2E headless cobre o fluxo principal da planilha e o recálculo oficial.

## Perguntas resolvidas

- A planilha não cria o projeto do zero; ela depende de configuração prévia.
- A planilha não importa avaliações de decisores.
- Não haverá aba por decisor.
- Critérios numéricos são únicos para o projeto.
- Critérios qualitativos aparecem só como referência.
- `q`, `p`, `v` podem ser preenchidos, mas são opcionais.
- `lambda` vazio usa `0.75`.
- Recálculo no resultado é oficial, não simulação temporária.
- Alterar número de classes preserva avaliações e recalcula apenas o resultado.

