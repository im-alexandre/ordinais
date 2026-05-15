# Design: Multiplos decisores no ELECTRE-MOr

Data: 2026-05-15
Status: aprovado para planejamento

## Contexto

O fluxo atual permite configurar projeto, criterios, alternativas, parametros e avaliacao em uma jornada unica. A nova funcionalidade deve permitir projetos com um decisor unico ou varios decisores independentes, sem transformar o caso simples em um fluxo burocratico.

O criador do projeto e o primeiro decisor. Ele pode continuar diretamente para a propria avaliacao ou adicionar outros decisores e enviar links individuais.

## Objetivos

- Permitir que o criador conclua sozinho um projeto com apenas um decisor.
- Permitir adicionar decisores convidados por links com token unico.
- Impedir que decisores convidados editem estrutura do projeto.
- Persistir respostas por decisor sem sobrescrever respostas de outros decisores.
- Agregar decisores ativos com peso igual antes do calculo ELECTRE-MOr.
- Liberar resultado somente por acao manual do criador.
- Permitir QR Code para compartilhamento dos links de avaliacao.

## Fora de escopo

- Login, senha ou contas de usuario.
- Peso configuravel por decisor.
- Permitir que convidados editem criterios, alternativas, classes ou parametros globais.
- Calculo automatico assim que todos concluirem.

## Fluxo de produto

1. O criador cria o projeto informando tambem o proprio nome como primeiro decisor.
2. O sistema cria o projeto e associa o criador como decisor ativo e marcado como criador.
3. Apos configurar estrutura e parametros globais, o criador pode:
   - continuar para a propria avaliacao; ou
   - adicionar decisores convidados.
4. Ao adicionar convidados, o sistema gera um token unico por decisor e exibe o link de avaliacao.
5. Depois de adicionar convidados, o criador pode ir direto para a propria avaliacao sem esperar que os convites sejam respondidos.
6. O criador pode copiar link, gerar QR Code ou desativar decisores pendentes.
7. Cada decisor convidado acessa seu link e preenche apenas a propria avaliacao.
8. O decisor pode reabrir o link e editar a propria resposta enquanto o resultado nao tiver sido gerado.
9. Quando todos os decisores ativos estiverem completos, o criador pode clicar em gerar resultado.
10. Apos gerar resultado, as avaliacoes usadas no calculo ficam travadas para preservar rastreabilidade.

## Modelo de dados

O projeto continua sendo dono de criterios, alternativas, classes, `lambda` e parametros `q/p/v`. Esses parametros sao globais e ficam sob controle do criador.

O decisor precisa representar coordenacao do fluxo coletivo:

- nome;
- projeto;
- token unico nao adivinhavel;
- status: pendente, em edicao, concluido ou desativado;
- flag para indicar o criador;
- timestamps de criacao, conclusao e desativacao.

As avaliacoes devem ser persistidas no escopo do decisor:

- comparacoes de criterios no escopo `(projeto, decisor)`;
- comparacoes qualitativas de alternativas no escopo `(projeto, decisor)`;
- notas numericas no escopo `(projeto, decisor, criterio, alternativa)`.

Como `AlternativaCriterio` hoje nao possui decisor, a implementacao deve incluir esse vinculo ou criar uma representacao equivalente que preserve notas numericas independentes por decisor.

## API

A API deve separar operacoes do criador e operacoes por token.

Operacoes do criador:

- listar decisores do projeto com status e links;
- adicionar decisores convidados;
- desativar decisores pendentes;
- obter link de avaliacao e dados para QR Code;
- gerar resultado manualmente;
- consultar resultado ou pendencias.

Operacoes por token:

- resolver contexto de avaliacao do decisor;
- salvar avaliacao do decisor de forma idempotente;
- marcar avaliacao como concluida;
- reabrir e editar a avaliacao enquanto o resultado nao estiver gerado.

O endpoint de resultado deve retornar `409` quando o resultado nao puder ser calculado. A resposta deve incluir quais decisores ativos ainda estao pendentes ou incompletos.

Regras de erro:

- token invalido: `404` ou `403`;
- decisor desativado: `410`;
- resultado ja gerado ou avaliacao travada: `409`;
- tentativa de convidado alterar estrutura do projeto: `403`;
- dados incompletos ao concluir avaliacao: `400` com campos pendentes.

## Agregacao e calculo

Todos os decisores ativos tem peso igual. A agregacao acontece antes do ELECTRE-MOr:

- comparar criterios por media das respostas normalizadas dos decisores ativos;
- comparar alternativas qualitativas por media das respostas dos decisores ativos;
- agregar notas numericas por media por `(criterio, alternativa)`;
- manter `q/p/v` e `lambda` globais do projeto.

O resultado so pode ser gerado quando todos os decisores ativos estiverem concluidos. Decisores desativados nao entram na completude nem na agregacao.

## Frontend

A tela de criacao/configuracao deve pedir o nome do criador como primeiro decisor. Depois da configuracao, ela deve oferecer:

- continuar para minha avaliacao;
- adicionar decisores;
- acessar gestao de links.

A gestao de links deve mostrar nome, status, link e acoes por decisor:

- copiar link;
- gerar QR Code;
- desativar pendente.

Depois de adicionar decisores, a gestao de links deve manter uma acao clara para o criador continuar imediatamente para a propria avaliacao. Essa acao nao depende de nenhum convidado ter aberto ou concluido o link.

O QR Code representa o mesmo link com token unico. Em desktop, o card ou modal pode mostrar QR Code e texto lado a lado. Em dispositivos moveis, o QR Code deve ficar maior no topo, e o texto como "Link de avaliacao de Ana Souza" junto das acoes deve ficar abaixo da imagem.

A tela de avaliacao deve resolver o decisor pelo estado do criador ou pelo token da URL. Convidados veem apenas campos de avaliacao e contexto necessario do projeto.

A tela de resultado deve mostrar pendencias por decisor enquanto houver decisores ativos incompletos. O botao "Gerar resultado" fica disponivel somente para o criador quando a completude estiver satisfeita.

## Testes e validacao

Backend:

- salvar avaliacao de um decisor sem sobrescrever outro decisor;
- validar completude por decisor;
- retornar `409` com pendencias no resultado;
- rejeitar token invalido, decisor desativado e avaliacao travada;
- agregar dois decisores ativos com peso igual;
- ignorar decisores desativados na completude e na agregacao.

Frontend:

- criar projeto com criador como primeiro decisor;
- seguir fluxo individual sem adicionar convidados;
- adicionar convidados e exibir links;
- gerar QR Code para link de decisor;
- aplicar layout mobile do QR Code com imagem grande no topo e texto abaixo;
- avaliar por token sem controles de estrutura;
- mostrar pendencias e habilitar geracao manual do resultado.

E2E em browser headless:

- criador cria projeto;
- criador adiciona ao menos um decisor convidado;
- criador avalia;
- convidado avalia pelo link;
- criador gera resultado;
- resultado exibe classificacoes finais.

## Criterios de aceite

- Projeto com um decisor permite seguir direto para avaliacao sem adicionar convidados.
- Projeto com varios decisores gera um link/token unico para cada convidado.
- Apos adicionar convidados, o criador pode ir direto para a propria avaliacao.
- QR Code e gerado a partir do link existente, sem criar outro token.
- Decisor convidado so avalia e nao altera estrutura do projeto.
- Respostas de um decisor nao sobrescrevem respostas de outro.
- Criador pode desativar decisores pendentes.
- Decisor pode editar a propria resposta antes da geracao do resultado.
- Resultado e gerado manualmente pelo criador.
- Resultado bloqueia com pendencias claras enquanto houver decisor ativo incompleto.
- Resultado usa media com peso igual entre decisores ativos.

## Revisao da spec

- Sem placeholders ou secoes incompletas.
- Escopo concentrado em decisores independentes, links, QR Code, persistencia por decisor e geracao manual.
- Regras de dados, API e frontend estao alinhadas com o fluxo aprovado.
- Ambiguidades principais foram fixadas: sem login, tokens unicos, convidados so avaliam, peso igual e QR Code client-side a partir do link.
