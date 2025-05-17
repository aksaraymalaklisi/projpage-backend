# Backend do projpage

O arquivo .env não é necessário, mas o projeto também não deverá rodar em produção sem ele.
Ele deve aceitar múltiplas entradas, mas normalmente, nada precisa ser feito se estiver em desenvolvimento.
Em produção, algumas entradas possuem fallback, como a database, que irá utilizar SQLite.
O resto precisa ser preenchido.

Esse é uma .env de exemplo. Lembre-se trocar quaisquer dados sensíveis (como o superuser, por exemplo) quando estiver em produção:

```bash
# Django settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# CORS and CSRF
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

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
DJANGO_STATIC_ROOT=/app/staticfiles

# Django superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword
```
Se estiver em DEBUG e quiser criar um perfil para o painel de administrador, você deve executar um comando para isso:
`python manage.py createsuperuser`

Em produção, gere uma nova chave secreta:
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`