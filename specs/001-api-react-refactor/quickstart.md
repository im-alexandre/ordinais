# Quickstart: Modernizacao da aplicacao ordinais

## 1. Preparar ambiente

```powershell
cd D:\ordinais
git status --short --branch
```

Confirmar que a branch ativa e `001-api-react-refactor`.

## 2. Primeira tarefa obrigatoria da implementacao

Antes de modificar qualquer view, modelo, URL ou dependencia, criar e executar a suite baseline:

```powershell
cd D:\ordinais\electre_mor
python manage.py test core.tests.test_url_baseline core.tests.test_url_flow_baseline
```

A suite deve chamar URLs por `django.test.Client`, registrar status, redirecionamentos, templates e marcadores de conteudo, e falhar se o comportamento conhecido mudar sem justificativa.

## 3. Modernizar dependencias

Atualizar runtime para Python 3.13 e dependencias compativeis com Django 5.2/DRF atual.

Verificacoes esperadas:

```powershell
cd D:\ordinais\electre_mor
python -m pip install -r requirements.txt
python manage.py check
python manage.py test
```

## 4. Validar contratos

Depois de implementar `core/api/`, validar os contratos planejados:

```powershell
cd D:\ordinais\electre_mor
python manage.py test core.tests.test_api_projects core.tests.test_api_participants core.tests.test_api_evaluations core.tests.test_api_result core.tests.test_api_contracts
```

## 5. Validar frontend

```powershell
cd D:\ordinais\electre_mor\frontend
npm install
npm run test
npm run build
```

O build deve ser copiado ou coletado para assets servidos pelo Django. A rota raiz deve carregar a interface React e preservar a inscricao da landing page com o acronimo em destaque.

Validar tambem a pagina estatica servida pelo Django:

```powershell
cd D:\ordinais\electre_mor
python manage.py test core.tests.test_frontend_static
```

## 6. Validar container e proxy

```powershell
cd D:\ordinais
docker compose build
docker compose up
```

Verificar:

- `electre_mor` continua expondo a porta usada pelo Traefik.
- labels `traefik.*` continuam presentes.
- banco usa versao compativel com Django 5.2.
- `/` serve o frontend.
- `/api/v1/projects/` responde pelo backend.

## 7. Executar localmente

```powershell
cd D:\ordinais\electre_mor
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Acessar:

- Interface: http://127.0.0.1:8000/
- API de projetos: http://127.0.0.1:8000/api/v1/projects/

## 8. Evidencia de documentacao

Para cada modificacao de classe, override ou API de Django/DRF, registrar no commit ou em notas de implementacao a documentacao oficial consultada. Fontes base iniciais:

- https://docs.djangoproject.com/en/5.2/releases/5.2/
- https://docs.djangoproject.com/en/5.2/topics/testing/tools/
- https://docs.djangoproject.com/en/5.2/howto/static-files/
- https://www.django-rest-framework.org/
- https://www.django-rest-framework.org/api-guide/generic-views/
- https://www.django-rest-framework.org/api-guide/viewsets/
- https://www.django-rest-framework.org/api-guide/routers/
