from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Просмотр доступен всем авторизованным
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            # Создание только для не-модераторов
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактирование для модераторов или владельцев
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            # Удаление только для владельцев (не модераторов)
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # Просмотр доступен всем авторизованным
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            # Создание только для не-модераторов
            return [IsAuthenticated(), ~IsModerator()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # Просмотр доступен всем авторизованным
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Редактирование для модераторов или владельцев
            return [IsAuthenticated(), IsModerator() | IsOwner()]
        elif self.request.method == 'DELETE':
            # Удаление только для владельцев
            return [IsAuthenticated(), ~IsModerator(), IsOwner()]
        return super().get_permissions()
