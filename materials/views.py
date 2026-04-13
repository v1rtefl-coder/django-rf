from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, CourseWithLessonsSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        # Для детального просмотра используем сериализатор с уроками
        if self.action == 'retrieve':
            return CourseWithLessonsSerializer
        # Для списка используем обычный сериализатор
        return CourseSerializer


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
