from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription
from users.models import User


@shared_task
def send_course_update_notification(course_id, updated_fields):
    """
    Отправляет уведомления подписчикам курса об обновлении
    """
    try:
        course = Course.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(course=course).select_related('user')

        if not subscribers.exists():
            return f"No subscribers for course {course.title}"

        updated_fields_str = ', '.join(updated_fields)
        subject = f"Обновление курса: {course.title}"
        message = f"""
        Здравствуйте!

        Курс "{course.title}" был обновлен.
        Обновленные поля: {updated_fields_str}

        Перейдите по ссылке, чтобы посмотреть обновления:
        {settings.SITE_URL}/api/courses/{course_id}/

        С уважением,
        Команда LMS
        """

        recipient_list = [sub.user.email for sub in subscribers]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f"Notifications sent to {len(recipient_list)} users for course {course.title}"

    except Course.DoesNotExist:
        return f"Course {course_id} not found"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"
