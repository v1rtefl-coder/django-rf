from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


# Сериализатор для краткой информации об уроке
class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'preview', 'video_link']


# Полный сериализатор для уроков
class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']

    def validate_video_link(self, value):
        """Валидация ссылки на видео"""
        validate_youtube_url(value)
        return value


# Базовый сериализатор для курса
class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'is_subscribed']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False


# Сериализатор для курса с уроками
class CourseWithLessonsSerializer(CourseSerializer):
    lessons = LessonShortSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['lessons']
