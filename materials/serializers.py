from rest_framework import serializers
from .models import Course, Lesson


# Сериализатор для краткой информации об уроке (для списка уроков в курсе)
class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'preview', 'video_link']


# Полный сериализатор для уроков (для отдельного эндпоинта)
class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


# Базовый сериализатор для курса (без уроков)
class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


# Сериализатор для курса с уроками
class CourseWithLessonsSerializer(CourseSerializer):
    lessons = LessonShortSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['lessons']
