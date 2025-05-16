# Backend do projpage

O arquivo .env não é necessário, mas o projeto também não deverá rodar em produção sem ele.
Ele deve aceitar múltiplas entradas, mas normalmente, nada precisa ser feito se estiver em desenvolvimento.
Em produção, algumas entradas possuem fallback, como a database, que irá utilizar SQLite.
O resto precisa ser preenchido.

Esse é uma .env de exemplo:

```
# Django settings 
# By default, the project uses DEBUG=True. It should be the opposite, though.
DJANGO_DEBUG=False 
DJANGO_SECRET_KEY=new-secret-key
DJANGO_ALLOWED_HOSTS=localhost, 127.0.0.1

# Database settings (used when DEBUG=False)
DJANGO_DB_ENGINE=django.db.backends.mysql
DJANGO_DB_NAME=example_db
DJANGO_DB_USER=django_user
DJANGO_DB_PASSWORD=pirimplimplim
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=3306

# Static files (this is optional, but may be useful)
DJANGO_STATIC_ROOT=/path/to/staticfiles

# CORS and CSRF - This is using localhost, which is probably not going to be the case in production.
CORS_ALLOWED_ORIGINS=http://localhost:3000, http://127.0.0.1:3000
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000, http://127.0.0.1:8000
```
