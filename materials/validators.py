import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет на YouTube
    """
    # Регулярное выражение для проверки YouTube ссылок
    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

    if not re.match(youtube_regex, value):
        raise serializers.ValidationError(
            'Разрешены только ссылки на YouTube. Пожалуйста, используйте ссылки вида '
            'https://www.youtube.com/watch?v=... или https://youtu.be/...'
        )

    return value
