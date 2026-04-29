from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import (
    UserSerializer, RegisterSerializer, PaymentInitiationSerializer,
    PaymentSessionSerializer, PaymentStatusSerializer
)
from .payment_service import create_payment_session, get_payment_status


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


@extend_schema(tags=["Платежи"])
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать сессию оплаты",
        description="Создает продукт, цену и сессию в Stripe для оплаты курса. Возвращает ссылку на оплату.",
        request=PaymentInitiationSerializer,
        responses={
            200: OpenApiResponse(response=PaymentSessionSerializer, description="Сессия создана"),
            400: OpenApiResponse(description="Ошибка в данных запроса"),
            401: OpenApiResponse(description="Неавторизован"),
            502: OpenApiResponse(description="Ошибка сервиса Stripe"),
        }
    )
    def post(self, request):
        serializer = PaymentInitiationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']

        try:
            result = create_payment_session(request.user, course_id, request)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )


@extend_schema(tags=["Платежи"])
class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверить статус платежа",
        description="Проверяет статус платежа в Stripe и в системе",
        responses={
            200: OpenApiResponse(response=PaymentStatusSerializer, description="Статус получен"),
            404: OpenApiResponse(description="Платеж не найден"),
        }
    )
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            stripe_status = get_payment_status(payment.stripe_session_id)

            # Обновляем статус в БД, если изменился
            if stripe_status and stripe_status.get('stripe_status') == 'paid':
                payment.status = 'paid'
                payment.save()

            serializer = PaymentStatusSerializer(payment)
            data = serializer.data
            if stripe_status:
                data['stripe_status'] = stripe_status

            return Response(data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Платеж не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=["Платежи"])
class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if session_id:
            try:
                payment = Payment.objects.get(stripe_session_id=session_id)
                payment.status = 'paid'
                payment.save()
                return Response({'message': 'Платеж успешно завершен'})
            except Payment.DoesNotExist:
                pass
        return Response({'message': 'Спасибо за оплату!'})


@extend_schema(tags=["Платежи"])
class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'Платеж отменен'})
