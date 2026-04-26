from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Lesson
from .serializers import CourseSerializer, CourseWithLessonsSerializer, LessonSerializer
from .paginators import CoursePaginator, LessonPaginator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseWithLessonsSerializer
        return CourseSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        # Проверка: модераторы не могут создавать курсы
        if request.user.groups.filter(name='moderators').exists():
            return Response(
                {"error": "Модераторы не могут создавать курсы"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        is_moderator = request.user.groups.filter(name='moderators').exists()
        is_owner = course.owner == request.user

        if not (is_moderator or is_owner):
            return Response(
                {"error": "Нет прав для редактирования этого курса"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        is_owner = course.owner == request.user

        if not is_owner:
            return Response(
                {"error": "Только владелец может удалить курс"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # Проверка: модераторы не могут создавать уроки
        if request.user.groups.filter(name='moderators').exists():
            return Response(
                {"error": "Модераторы не могут создавать уроки"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        lesson = self.get_object()
        is_moderator = request.user.groups.filter(name='moderators').exists()
        is_owner = lesson.owner == request.user

        print(f"DEBUG: User: {request.user.email}")
        print(f"DEBUG: Lesson owner: {lesson.owner.email if lesson.owner else 'None'}")
        print(f"DEBUG: is_moderator: {is_moderator}")
        print(f"DEBUG: is_owner: {is_owner}")

        if not (is_moderator or is_owner):
            return Response(
                {"error": "Нет прав для редактирования этого урока"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        is_owner = lesson.owner == request.user

        if not is_owner:
            return Response(
                {"error": "Только владелец может удалить урок"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
