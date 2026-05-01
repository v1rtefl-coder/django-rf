from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import User


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, которые не заходили более месяца и активны
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True,
        is_superuser=False  # Не блокируем суперпользователей
    )

    count = inactive_users.count()

    # Обновляем статус (батчем)
    inactive_users.update(is_active=False)

    return f"Deactivated {count} inactive users (last login before {one_month_ago})"


@shared_task
def check_user_activity():
    """
    Проверяет активность пользователей и отправляет предупреждения
    """
    twenty_days_ago = timezone.now() - timedelta(days=20)

    warning_users = User.objects.filter(
        last_login__lt=twenty_days_ago,
        last_login__gte=twenty_days_ago - timedelta(days=10),
        is_active=True,
        is_superuser=False
    )

    for user in warning_users:
        # Здесь можно отправить предупреждение на email
        print(f"Warning: User {user.email} will be deactivated in 10 days")

    return f"Found {warning_users.count()} users to warn"
