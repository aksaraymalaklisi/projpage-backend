# Backend do projpage

Esse README inclui instruções para rodar o backend do projpage. O backend possui pouquíssimas funcionalidades, mas essas instruções servem para prepará-lo para produção.

## O arquivo .env

O arquivo .env não é necessário, mas o projeto não irá rodar em produção sem ele configurado.
Ele deve aceitar múltiplas entradas, mas normalmente, nada precisa ser feito se estiver em desenvolvimento.
Em produção, algumas entradas possuem fallback, como a database, que irá utilizar SQLite.
O resto precisa ser preenchido.

Esse é uma .env de exemplo. Lembre-se trocar quaisquer dados sensíveis (como a chave de produção e o superuser, por exemplo) quando estiver em produção:

```bash
# Django settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# CORS and CSRF
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# Database settings (used when DEBUG=False)
# MySQL seems to require a root password
DJANGO_DB_ENGINE=django.db.backends.mysql
DJANGO_DB_NAME=example_db
DJANGO_DB_USER=django_user
DJANGO_DB_PASSWORD=pirimplimplim
DJANGO_DB_HOST=db
DJANGO_DB_PORT=3306
DJANGO_DB_ROOT_PASSWORD=pirimplimplim_mysql

# Static files (optional)
DJANGO_STATIC_ROOT=/static/

# Media files root
DJANGO_MEDIA_ROOT=/media/

# Django superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword
```

Se estiver em DEBUG e quiser criar um perfil para o painel de administrador, você deve executar um comando para isso:
`python manage.py createsuperuser`

Em produção, gere uma nova chave secreta:
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## Rodando o backend com Docker

Esteja com Docker instalado (com Docker Compose, mas assumo que já venha instalado).
O Docker Compose atual utiliza Nginx para servir os arquivos.
Se estiver rodando em produção, é necessário ter o arquivo de configuração do Nginx ou utilizar o próprio webserver.
Whitenoise foi removido, já que ele não servia os arquivos de mídia (arquivos .gpx).

1. **Configure o arquivo `.env`**
   Use o exemplo acima e crie `.env` na raiz do projeto. Altere tudo que achar necessário.

2. **Construa a imagem Docker**
   No terminal, execute:

   ```sh
   docker-compose build
   ```

3. **Inicie os serviços**  

   ```sh
   docker-compose up -d
   ```

   O backend estará disponível em [http://localhost:8080](http://localhost:8080) e na porta 8000 (gunicorn). Note que gunicorn não está servindo arquivos estáticos.
   Se estiver com um webserver já configurado, aponte-o para a porta 8000, como visto na .conf do Nginx.
   Use o argumento `-d` para rodar em modo headless.
4. **Acessando o banco de dados**
   O banco MySQL estará disponível no serviço `db` na porta 3306 (internamente), mas caso queira realizar alguma mudança no banco de dados (que não é ideal, pois estamos usando Django), acesse pelo shell do MySQL.

5. **Parando os serviços**
   Para parar os containers:

   ```sh
   docker-compose down
   ```

### Utilidades

Algumas ações que normalmente seriam feitas pelo terminal não poderiam ser realizadas no Docker. Note que, através do bash (terminal) você também poderá acessar o shell da database pelo Django, mas você também pode usar o `exec` para isso.

- Para ver os logs:
  
  ```sh
  docker-compose logs -f
  ```

- Para acessar o bash do container:

  ```sh
  docker-compose exec web bash
  ```

- Para acessar o shell do Django:
  
  ```sh
  docker-compose exec web python manage.py shell
  ```

---

## Exemplos de uso da API (Autenticação e Ratings)

### 1. Registro de usuário

**POST** `/register/`

Body (JSON):

```json
{
  "username": "henrique",
  "email": "henrique@email.com",
  "password": "famosissima-senha-segura",
  "name": "Henrique Roberto",
  "phone": "11999999999",
  "cpf": "123.456.789-00"
}
```

### 2. Login (obter tokens JWT)

**POST** `/login/`

Body (JSON):

```json
{
  "username": "henrique",
  "password": "famosissima-senha-segura"
}
```

Resposta:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### 3. Usando o token de acesso

Para acessar rotas protegidas, envie o header:

`Authorization: Bearer <access_token>`

No Postman, adicione em Headers:

- Key: `Authorization`
- Value: `Bearer <access_token>`

### 4. Refresh do token

**POST** `/token/refresh/`

Body (JSON):

```json
{
  "refresh": "<refresh_token>"
}
```

Resposta:

```json
{
  "access": "<novo_access_token>"
}
```

### 5. Consultar/editar perfil do usuário autenticado

**GET** `/users/me/`  
Headers: `Authorization: Bearer <access_token>`

**PATCH** `/users/me/`  
Headers: `Authorization: Bearer <access_token>`
Body (JSON):

```json
{
  "name": "Henrique 2.0",
  "phone": "11888888888"
}
```

### 6. Criar uma avaliação (rating) de uma trilha

**POST** `/ratings/`  
Headers: `Authorization: Bearer <access_token>`
Body (JSON):

```json
{
  "track": 1,
  "comment": "Trilha excelente!",
  "score": 5
}
```

### 7. Listar avaliações de uma trilha

**GET** `/ratings/?track=1`

### 8. Editar ou apagar sua avaliação

**PATCH** `/ratings/<id>/`  
Headers: `Authorization: Bearer <access_token>`
Body (JSON):

```json
{
  "comment": "Comentário atualizado"
}
```

**DELETE** `/ratings/<id>/`  
Headers: `Authorization: Bearer <access_token>`

---

Se receber "Authentication credentials were not provided.", confira se está enviando o header.

---
