# Data Model: Modernizacao da aplicacao ordinais

## Projeto

**Representa**: Uma sessao de avaliacao ordinal.

**Campos**:

- `id`: identificador unico.
- `nome`: nome curto do projeto.
- `descricao`: texto explicativo.
- `qtde_classes`: quantidade de classes de classificacao, minimo 2.
- `qtde_criterios`: quantidade de criterios, minimo 2.
- `qtde_alternativas`: quantidade de alternativas, minimo 2.
- `qtde_decisores`: quantidade de decisores, minimo 1.
- `lamb`: nivel de corte entre 0.5 e 1.
- `data`: data de criacao.

**Relacionamentos**: Tem muitos decisores, criterios, alternativas, avaliacoes e parametros.

**Validacoes**:

- `qtde_classes` nao pode exceder `qtde_alternativas`.
- Campos quantitativos devem respeitar minimos atuais.

## Decisor

**Representa**: Pessoa ou papel que informa preferencias.

**Campos**:

- `id`
- `projeto`
- `nome`

**Validacoes**:

- Nome unico dentro do projeto.

## Criterio

**Representa**: Fator usado para avaliar alternativas.

**Campos**:

- `id`
- `projeto`
- `nome`
- `numerico`: indica se a nota vem de valor direto ou comparacao qualitativa.
- `monotonico`: beneficio/custo.

**Validacoes**:

- Nome unico dentro do projeto.
- `monotonico` deve aceitar apenas valores suportados.

## Alternativa

**Representa**: Opcao avaliada.

**Campos**:

- `id`
- `projeto`
- `nome`

**Validacoes**:

- Nome unico dentro do projeto.

## AlternativaCriterio

**Representa**: Nota numerica de uma alternativa em um criterio.

**Campos**:

- `id`
- `projeto`
- `criterio`
- `alternativa`
- `nota`

**Validacoes**:

- O criterio e a alternativa devem pertencer ao mesmo projeto.
- Deve existir para combinacoes numericas exigidas pelo fluxo.

## AvaliacaoCriterios

**Representa**: Preferencia pareada entre dois criterios para um decisor.

**Campos**:

- `id`
- `projeto`
- `decisor`
- `criterioA`
- `criterioB`
- `nota`

**Validacoes**:

- Decisor e criterios devem pertencer ao mesmo projeto.
- `nota` deve permanecer na escala atual de comparacao.
- A avaliacao inversa deve ser representada ou derivada de forma consistente.

## AvaliacaoAlternativas

**Representa**: Preferencia pareada entre duas alternativas em um criterio qualitativo.

**Campos**:

- `id`
- `projeto`
- `decisor`
- `criterio`
- `alternativaA`
- `alternativaB`
- `nota`

**Validacoes**:

- Decisor, criterio e alternativas devem pertencer ao mesmo projeto.
- `nota` deve permanecer na escala atual de comparacao.
- A avaliacao inversa deve ser representada ou derivada de forma consistente.

## CriterioParametro

**Representa**: Parametros `p`, `q` e `v` usados pelo calculo de classificacao.

**Campos**:

- `id`
- `projeto`
- `criterio`
- `p`
- `q`
- `v`

**Validacoes**:

- Criterio deve pertencer ao projeto.
- Parametros devem ser numericos e coerentes com o metodo.

## Resultado de Avaliacao

**Representa**: Saida calculada para exibicao e API.

**Campos derivados**:

- pesos dos criterios.
- pontuacao das alternativas.
- classificacao otimista e pessimista.
- classificacao por metodo range e quantile quando aplicavel.
- mensagens de inconsistencia ou dados insuficientes.

**Persistencia**: Pode ser derivado sob demanda a partir do projeto e das avaliacoes, mantendo arquivos de download apenas quando o fluxo exigir.

## Baseline de Rotas

**Representa**: Registro esperado do comportamento das URLs antes da refatoracao.

**Campos**:

- `path`
- `method`
- `status_code`
- `redirect_chain`
- `template_names`
- `content_markers`
- `response_headers`
- `notes`

**Persistencia**: Artefato de teste versionado, preferencialmente fixture JSON dentro da suite de testes.

## Transicoes de Estado

1. Projeto criado.
2. Decisores, criterios e alternativas cadastrados.
3. Valores numericos por alternativa/criterio informados quando existirem criterios numericos.
4. Criterios avaliados por decisor.
5. Alternativas avaliadas por criterio qualitativo quando existirem criterios qualitativos.
6. Parametros de criterios informados.
7. Resultado calculado e exibido.
