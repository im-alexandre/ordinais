# Deploy Ordinais no Coolify via API

## Resumo

- Fazer o deploy depois que a branch `001-api-react-refactor` estiver finalizada, criando a branch remota `coolify` a partir dela e incluindo o frontend React.
- Criar no Coolify o projeto `ordinais`, ambiente `prod`, aplicação Docker Compose apontando para `im-alexandre/ordinais`, branch `coolify`, domínio `https://electremor.drg.ink`.
- Usar `server_uuid=uswc0ggc0wwo0g8wc0oscwwo` e `github_app_uuid=c8k8s8wcw8kksg4ws8gc8w0s`.
- Não reutilizar o GitHub App do plugin Codex; o Coolify usará a GitHub App já existente nele.

## Mudanças no Repositório

- Criar `.env` local com segredos gerados e variáveis de runtime; manter fora do Git. O `.gitignore` já cobre `.env*`.
- Ajustar `docker-compose.yml` para não depender de `./electre_mor/env.electre`; usar variáveis interpoladas por `.env` local e por envs cadastradas no Coolify.
- Definir variáveis:
  - `SQL_ENGINE=django.db.backends.postgresql`
  - `SQL_HOST=db_electre`
  - `SQL_PORT=5432`
  - `POSTGRES_USER=electremor`
  - `POSTGRES_PASSWORD=<gerar chave forte>`
  - `POSTGRES_DB=electremor`
  - `SECRET_KEY=<gerar chave forte>`
  - `DEBUG=1`
  - `ALLOWED_HOSTS=localhost,127.0.0.1,coolify.drg.ink,electremor.drg.ink`
- Atualizar o Dockerfile para build compatível com Django 5.x e React: base Python 3.12+, build do frontend Vite, cópia do bundle para os estáticos Django antes do `collectstatic`.

## Fluxo Coolify

- Preflight: confirmar que não existe projeto/app/domínio conflitante; hoje não há `ordinais` nem `electremor.drg.ink` cadastrado.
- Criar projeto via `POST /projects` com `name=ordinais`.
- Criar ambiente via `POST /projects/{project_uuid}/environments` com `name=prod`.
- Criar aplicação via `POST /applications/private-github-app` com:
  - `project_uuid`
  - `server_uuid=uswc0ggc0wwo0g8wc0oscwwo`
  - `environment_name=prod`
  - `github_app_uuid=c8k8s8wcw8kksg4ws8gc8w0s`
  - `git_repository=im-alexandre/ordinais`
  - `git_branch=coolify`
  - `build_pack=dockercompose`
  - `docker_compose_location=docker-compose.yml`
  - `ports_exposes=80`
  - `docker_compose_domains=[{"name":"electre_mor","domain":"https://electremor.drg.ink"}]`
  - `is_auto_deploy_enabled=true`
  - `is_force_https_enabled=true`
  - `instant_deploy=true`
- Cadastrar/atualizar as mesmas variáveis da `.env` na aplicação pelo endpoint bulk de envs do Coolify.

## Testes e Validação

- Antes de subir: `docker compose config`, build local do Docker Compose, testes Django e testes frontend.
- Depois do deploy: verificar logs do Coolify, status do deployment, acesso a `https://electremor.drg.ink`, rota raiz servindo shell React e API em `/api/v1/`.
- Validar que a branch remota `coolify` existe e que a GitHub App do Coolify enxerga `im-alexandre/ordinais`.

## Assumptions

- `DEBUG=1` fica intencionalmente mantido conforme sua escolha, apesar de não ser o padrão recomendado para produção.
- A branch `coolify` será criada somente quando a implementação em `001-api-react-refactor` estiver pronta.
- A chave de API do Coolify não será gravada no `.env` da aplicação; usar apenas como segredo operacional durante a automação. Como ela foi enviada no chat, o ideal é rotacioná-la após concluir o deploy.
- Referências usadas: [Create Project](https://next.coolify.io/docs/api-reference/api/operations/create-project), [Create Environment](https://next.coolify.io/docs/api-reference/api/operations/create-environment), [Create Private GitHub App Application](https://next.coolify.io/docs/api-reference/api/operations/create-private-github-app-application), [Docker Compose no Coolify](https://coolify.io/docs/knowledge-base/docker/compose).
