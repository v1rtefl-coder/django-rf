from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create sample payments'

    def handle(self, *args, **options):
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('No users found'))
            return

        payments_data = [
            {'user': user, 'course': course, 'amount': 5000.00, 'payment_method': 'transfer'},
            {'user': user, 'lesson': lesson, 'amount': 1500.00, 'payment_method': 'cash'},
            {'user': user, 'course': course, 'amount': 5000.00, 'payment_method': 'cash'},
        ]

        for data in payments_data:
            payment, created = Payment.objects.get_or_create(**data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Payment created: {payment}'))
            else:
                self.stdout.write(f'Payment already exists: {payment}')

        self.stdout.write(self.style.SUCCESS(f'Total payments: {Payment.objects.count()}'))
