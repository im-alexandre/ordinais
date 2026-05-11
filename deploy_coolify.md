# Deploy Ordinais no Coolify via API

## Resumo

- Fazer o deploy da branch `master`, que já contém a refatoração Django 5.x + React.
- Criar no Coolify o projeto `ordinais`, ambiente `prod`, aplicação Docker Compose apontando para `im-alexandre/ordinais`, branch `master`, domínio `https://electremor.drg.ink`.
- Usar `server_uuid=uswc0ggc0wwo0g8wc0oscwwo` e `github_app_uuid=c8k8s8wcw8kksg4ws8gc8w0s`.
- Não reutilizar o GitHub App do plugin Codex; o Coolify usará a GitHub App já existente nele.

## Estado do Repositório

- `docker-compose.yml` é a fonte de configuração do Coolify e não depende de `env_file`.
- `.env.example` documenta as variáveis esperadas; `.env` local continua fora do Git.
- `electre_mor/Dockerfile` gera uma imagem autocontida: instala dependências Python, executa o build Vite e coleta arquivos estáticos Django.
- `electre_mor/entrypoint_electre.sh` aplica migrações com `migrate --noinput` e sobe o Gunicorn na porta `80`.

## Variáveis de Runtime

Cadastrar no Coolify, na aplicação, as variáveis abaixo:

```env
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=db_electre
SQL_PORT=5432

POSTGRES_USER=electremor
POSTGRES_PASSWORD=<gerar chave forte>
POSTGRES_DB=electremor

DEBUG=1
SECRET_KEY=<gerar chave forte>
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,coolify.drg.ink,electremor.drg.ink
```

`DEBUG=1` fica intencionalmente mantido para este deploy, conforme decisão operacional atual. Para endurecimento posterior, trocar para `DEBUG=0` e revisar hosts, cookies e headers de segurança.

## Fluxo Coolify

1. Preflight:
   - Confirmar que `origin/master` está atualizado.
   - Confirmar que não há projeto/app/domínio conflitante para `ordinais` e `electremor.drg.ink`.
   - Confirmar que o GitHub App do Coolify enxerga `im-alexandre/ordinais`.

2. Criar projeto via `POST /projects`:
   - `name=ordinais`

3. Criar ambiente via `POST /projects/{project_uuid}/environments`:
   - `name=prod`

4. Criar aplicação via `POST /applications/private-github-app`:
   - `project_uuid=<uuid do projeto ordinais>`
   - `server_uuid=uswc0ggc0wwo0g8wc0oscwwo`
   - `environment_name=prod`
   - `github_app_uuid=c8k8s8wcw8kksg4ws8gc8w0s`
   - `git_repository=im-alexandre/ordinais`
   - `git_branch=master`
   - `build_pack=dockercompose`
   - `docker_compose_location=docker-compose.yml`
   - `ports_exposes=80`
   - `docker_compose_domains=[{"name":"electre_mor","domain":"https://electremor.drg.ink"}]`
   - `is_auto_deploy_enabled=true`
   - `is_force_https_enabled=true`
   - `instant_deploy=true`

5. Cadastrar variáveis em lote pelo endpoint de envs da aplicação.

## Testes e Validação

Antes de subir:

```powershell
Copy-Item .env.example .env
docker compose --env-file .env config
docker compose --env-file .env build
```

Validar também:

- Testes Django.
- Testes frontend.
- A imagem deve funcionar sem bind mount de código.

Depois do deploy:

- Verificar logs do Coolify.
- Confirmar status de deployment concluído.
- Testar `https://electremor.drg.ink`.
- Confirmar shell React na rota raiz.
- Confirmar API em `/api/v1/`.
- Criar/consultar um projeto para validar persistência no Postgres.

## Assumptions

- A chave de API do Coolify não deve ser gravada no `.env` da aplicação; usar apenas como segredo operacional durante a automação.
- Como qualquer chave enviada em chat pode estar comprometida, rotacionar a chave de API do Coolify após concluir o deploy.
- Referências: [Create Project](https://next.coolify.io/docs/api-reference/api/operations/create-project), [Create Environment](https://next.coolify.io/docs/api-reference/api/operations/create-environment), [Create Private GitHub App Application](https://next.coolify.io/docs/api-reference/api/operations/create-private-github-app-application), [Update Envs Bulk](https://coolify.io/docs/api-reference/api/operations/update-envs-by-application-uuid), [Docker Compose no Coolify](https://coolify.io/docs/knowledge-base/docker/compose).
