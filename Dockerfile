FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_clubs && python manage.py shell -c \"from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists() or U.objects.create_superuser(email='$DJANGO_SUPERUSER_EMAIL', password='$DJANGO_SUPERUSER_PASSWORD', name='Admin')\" && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2"]