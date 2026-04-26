from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User
from materials.models import Course, Lesson, Subscription


class LessonTests(APITestCase):

    def setUp(self):
        # Создание групп
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')

        # Создание пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='user123',
            first_name='Test',
            last_name='User'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='moderator123',
            first_name='Moderator',
            last_name='User'
        )
        self.moderator.groups.add(self.moderator_group)

        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='owner123',
            first_name='Owner',
            last_name='User'
        )

        # Создание курса
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.owner
        )

        # Создание урока
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner
        )

        # Настройка клиентов
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)

        self.owner_client = APIClient()
        self.owner_client.force_authenticate(user=self.owner)

    def test_create_lesson_as_user(self):
        """Тест создания урока обычным пользователем"""
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        lesson = Lesson.objects.last()
        self.assertEqual(lesson.owner, self.user)

    def test_create_lesson_with_invalid_url(self):
        """Тест создания урока с недопустимой ссылкой"""
        url = reverse('lesson-list-create')
        data = {
            'title': 'Invalid URL Lesson',
            'description': 'Should fail',
            'video_link': 'https://rutube.ru/video/test',
            'course': self.course.id
        }
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_update_lesson_as_owner(self):
        """Тест обновления урока владельцем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Title'}
        response = self.owner_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Title')

    def test_update_lesson_as_user(self):
        """Тест запрета обновления чужого урока обычным пользователем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Should not update'}
        response = self.user_client.patch(url, data, format='json')
        # Обычный пользователь не может редактировать чужой урок
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_owner(self):
        """Тест удаления урока владельцем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.owner_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_as_user(self):
        """Тест запрета удаления чужого урока обычным пользователем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons(self):
        """Тест получения списка уроков"""
        url = reverse('lesson-list-create')
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        url = reverse('subscribe')
        data = {'course_id': self.course.id}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('subscribe')
        data = {'course_id': self.course.id}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_without_course_id(self):
        """Тест подписки без указания course_id"""
        url = reverse('subscribe')
        data = {}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_has_subscription_field(self):
        """Тест наличия поля подписки в курсе"""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('course-list')
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что поле is_subscribed существует в ответе
        if response.data.get('results'):
            self.assertIn('is_subscribed', response.data['results'][0])

    def test_subscription_toggle_twice(self):
        """Тест переключения подписки (добавление и удаление)"""
        url = reverse('subscribe')
        data = {'course_id': self.course.id}

        # Первый запрос - создание подписки
        response1 = self.user_client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)

        # Второй запрос - удаление подписки
        response2 = self.user_client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_lesson_pagination(self):
        """Тест пагинации уроков"""
        # Создаем 15 уроков
        for i in range(15):
            Lesson.objects.create(
                title=f'Lesson {i}',
                description='Test',
                video_link='https://www.youtube.com/watch?v=test',
                course=self.course,
                owner=self.owner
            )

        url = reverse('lesson-list-create')
        response = self.user_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
