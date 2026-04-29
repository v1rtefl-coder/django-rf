from rest_framework import serializers
from .models import User, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'city']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class PaymentInitiationSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(help_text="ID курса для оплаты")

class PaymentSessionSerializer(serializers.Serializer):
    session_id = serializers.CharField(help_text="ID сессии в Stripe")
    checkout_url = serializers.URLField(help_text="Ссылка для перехода на оплату")
    payment_id = serializers.IntegerField(help_text="ID платежа в системе")

class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'status', 'amount', 'created_at', 'updated_at']
