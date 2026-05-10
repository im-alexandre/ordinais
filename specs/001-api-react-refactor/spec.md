# Feature Specification: Modernizacao da aplicacao ordinais

**Feature Branch**: `001-api-react-refactor`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Criar testes exploratorios antes de modificar views, modernizar dependencias para Django 5.x, refatorar o projeto para uma API consumida por frontend React, remover django-pandas, manter compatibilidade Coolify/Traefik, servir o build frontend pelo proprio Django e preservar a inscricao da landing page com visual mais tech/prime claro."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preservar comportamento existente das rotas (Priority: P1)

Como pessoa responsavel pela aplicacao, quero registrar o comportamento atual das paginas e fluxos por chamadas diretas as URLs antes de qualquer refatoracao, para garantir que a modernizacao nao altere resultados esperados nem quebre jornadas existentes.

**Why this priority**: A refatoracao so e aceitavel se houver uma linha de base objetiva para comparar o comportamento antes e depois das mudancas.

**Independent Test**: Pode ser testado executando a suite exploratoria inicial contra todas as URLs relevantes e verificando que ela registra status, redirecionamentos, conteudo essencial e respostas esperadas.

**Acceptance Scenarios**:

1. **Given** a aplicacao atual disponivel, **When** as URLs publicas e fluxos principais forem chamadas pela suite exploratoria, **Then** os comportamentos observados devem ser registrados como baseline verificavel.
2. **Given** a refatoracao concluida, **When** a mesma suite exploratoria for executada novamente, **Then** as URLs equivalentes devem manter os resultados esperados ou apresentar diferencas explicitamente justificadas pela especificacao.
3. **Given** uma rota existente com entrada invalida, **When** a suite exercitar o caso de erro correspondente, **Then** o sistema deve retornar uma resposta compreensivel e consistente com o comportamento baseline.

---

### User Story 2 - Consumir funcionalidades por interface web moderna (Priority: P2)

Como usuario final, quero acessar uma interface clara e moderna para informar dados, executar metodos ordinais e visualizar resultados, para concluir a avaliacao sem depender da experiencia visual antiga.

**Why this priority**: O principal valor percebido pelo usuario vem da continuidade dos fluxos de avaliacao em uma interface mais simples, clara e confiavel.

**Independent Test**: Pode ser testado acessando a pagina inicial servida pela aplicacao, preenchendo um fluxo representativo de avaliacao e confirmando que o resultado fica disponivel sem erros visuais ou de navegacao.

**Acceptance Scenarios**:

1. **Given** a pagina inicial carregada, **When** o usuario visualizar a landing page, **Then** o nome do metodo deve aparecer com o acronimo em destaque e com identidade visual clara, tecnologica e premium.
2. **Given** dados validos de criterios e alternativas, **When** o usuario concluir o fluxo de avaliacao, **Then** o sistema deve apresentar o resultado correspondente de forma legivel e rastreavel.
3. **Given** dados incompletos ou invalidos, **When** o usuario tentar prosseguir, **Then** a interface deve explicar o problema e indicar quais campos precisam de correcao.

---

### User Story 3 - Expor funcionalidades para consumo estruturado (Priority: P3)

Como integrador ou manutentor, quero que as funcionalidades principais estejam disponiveis por contratos de dados estruturados, para permitir manutencao, testes automatizados e evolucao do frontend sem acoplamento a paginas antigas.

**Why this priority**: A separacao entre experiencia visual e funcionalidades de negocio reduz risco de regressao e facilita futuras integracoes.

**Independent Test**: Pode ser testado chamando os contratos de dados documentados com entradas validas e invalidas e verificando respostas, mensagens de erro e consistencia com os fluxos de usuario.

**Acceptance Scenarios**:

1. **Given** uma requisicao valida para criar ou avaliar um projeto ordinal, **When** o contrato correspondente for chamado, **Then** a resposta deve conter os dados necessarios para continuidade do fluxo.
2. **Given** uma requisicao com dados invalidos, **When** o contrato correspondente for chamado, **Then** a resposta deve identificar os campos problematicos de forma objetiva.
3. **Given** a aplicacao implantada no ambiente de hospedagem atual, **When** ela receber trafego roteado pelo proxy configurado, **Then** as paginas e contratos de dados devem permanecer acessiveis pelos dominios esperados.

### Edge Cases

- A suite baseline encontra rotas removidas, renomeadas ou dependentes de dados ausentes.
- Usuarios enviam matrizes, criterios ou alternativas com tamanhos minimos, maximos ou inconsistentes.
- Resultados calculados contem empates, ausencia de vencedor claro ou dados insuficientes para ranking.
- O build visual estatico esta ausente, desatualizado ou inacessivel no ambiente de producao.
- A aplicacao recebe cabecalhos de proxy ou dominio publico diferentes entre ambiente local e hospedado.
- Dependencias antigas deixam de oferecer comportamento equivalente nas versoes modernizadas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish an exploratory baseline for existing route behavior before any application behavior is modified.
- **FR-002**: System MUST allow the same exploratory route tests to be executed after the refactor and compare outcomes against the baseline.
- **FR-003**: System MUST preserve all user-visible route behaviors that are not explicitly replaced by equivalent modern flows.
- **FR-004**: System MUST expose the main ordinal evaluation capabilities through structured request and response contracts suitable for a separate visual interface.
- **FR-005**: System MUST provide clear validation feedback for invalid criteria, alternatives, weights, rankings, or incomplete evaluation inputs.
- **FR-006**: System MUST remove reliance on spreadsheet-style helper dependencies when equivalent native data processing is sufficient for the application behavior.
- **FR-007**: System MUST run on supported current runtime and dependency versions compatible with the selected modern web platform.
- **FR-008**: System MUST keep the deployment service definitions compatible with the existing managed hosting and reverse-proxy setup.
- **FR-009**: System MUST provide a modern visual frontend that consumes the structured contracts for all primary user workflows.
- **FR-010**: System MUST serve the production frontend as a static page from the same web application entry point used for the backend service.
- **FR-011**: System MUST preserve the landing-page inscription where the method name is shown with its acronym emphasized.
- **FR-012**: System MUST present the refreshed interface with a light, premium, technology-oriented visual style.
- **FR-013**: System MUST document each significant modernization decision with direct reference to the authoritative framework documentation consulted during implementation.
- **FR-014**: System MUST avoid custom behavior that duplicates supported capabilities already available in the selected web framework or data-contract framework.
- **FR-015**: System MUST keep existing calculation semantics for ordinal methods unless a difference is documented as a correction and covered by tests.

### Key Entities

- **Projeto de Avaliacao**: Represents a user evaluation session, including title or context, configured criteria, alternatives, and selected method.
- **Criterio**: Represents a decision factor used to evaluate alternatives, including name, direction, weight or ordering information when applicable.
- **Alternativa**: Represents an option being compared across criteria.
- **Entrada de Avaliacao**: Represents submitted values, rankings, preferences, or pairwise data required by an ordinal method.
- **Resultado de Avaliacao**: Represents calculated ordering, scores, ties, winners, explanatory details, and validation messages.
- **Baseline de Rotas**: Represents the captured expected behavior for existing URLs, including status codes, redirects, key content, and relevant response metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of route behaviors captured in the initial baseline either pass unchanged after refactoring or have an approved equivalence note.
- **SC-002**: At least 95% of representative valid evaluation flows can be completed from landing page to result without manual intervention or unexpected errors.
- **SC-003**: Users receive actionable validation feedback for invalid evaluation submissions in every primary workflow tested.
- **SC-004**: The refreshed landing experience clearly displays the method inscription and acronym emphasis on desktop and mobile viewports.
- **SC-005**: The production deployment exposes both the visual interface and structured data contracts through the expected public route configuration.
- **SC-006**: Dependency modernization is complete with no remaining dependency on deprecated or removed packages identified in the request.
- **SC-007**: Documentation consultation evidence exists for every significant framework-level class, function, or override decision made during implementation.

## Assumptions

- The existing application behavior is the source of truth unless the implementation uncovers a defect that must be explicitly documented and tested.
- The primary users are people evaluating ordinal decision methods through a web interface.
- The refreshed frontend should replace the old visual experience for public flows while preserving equivalent business outcomes.
- The deployment target remains the current managed container environment with the existing reverse-proxy model.
- The requested technology choices are treated as implementation constraints for planning, while this specification focuses on observable behavior and success outcomes.
