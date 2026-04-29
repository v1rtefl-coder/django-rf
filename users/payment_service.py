import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import APIException
from users.models import Payment
from materials.models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeServiceError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Сервис оплаты временно недоступен'
    default_code = 'stripe_error'


def create_payment_session(user, course_id, request):
    """
    Создает продукт, цену и сессию Stripe для оплаты курса
    """
    course = get_object_or_404(Course, id=course_id)

    # Проверяем, есть ли уже оплаченный платеж
    if Payment.objects.filter(user=user, course=course, status='paid').exists():
        raise StripeServiceError(detail='Этот курс уже оплачен')

    try:
        # 1. Создаем продукт в Stripe
        product = stripe.Product.create(
            name=course.title,
            description=course.description[:500] if course.description else None,
            metadata={
                'course_id': course.id,
                'site': 'django-rf-lms'
            }
        )

        # 2. Создаем цену (сумма в копейках!)
        amount_kopecks = int(course.price * 100) if hasattr(course, 'price') else 10000  # 100 руб по умолчанию

        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount_kopecks,
            currency='rub',
            metadata={
                'course_id': course.id
            }
        )

        # 3. Формируем URL для редиректа
        base_url = request.build_absolute_uri('/').rstrip('/')
        success_url = f"{base_url}/payment/success/"
        cancel_url = f"{base_url}/payment/cancel/"

        # 4. Создаем сессию оплаты
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price.id, 'quantity': 1}],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
                'course_id': course.id,
                'user_email': user.email
            },
            customer_email=user.email
        )

        # 5. Сохраняем информацию о платеже в БД
        payment = Payment.objects.create(
            user=user,
            course=course,
            stripe_session_id=checkout_session.id,
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            checkout_url=checkout_session.url,
            amount=amount_kopecks / 100,  # Конвертируем обратно в рубли
            amount_kopecks=amount_kopecks,
            status='pending'
        )

        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url,
            'payment_id': payment.id
        }

    except stripe.error.StripeError as e:
        print(f"Stripe error: {e.user_message}")
        raise StripeServiceError(detail=str(e.user_message))
    except Exception as e:
        print(f"Error: {str(e)}")
        raise StripeServiceError(detail=f"Не удалось создать платеж: {str(e)}")


def get_payment_status(session_id):
    """
    Получает статус платежа из Stripe
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'stripe_status': session.payment_status,
            'stripe_status_code': session.status,
            'customer_email': session.customer_email
        }
    except stripe.error.StripeError as e:
        return None