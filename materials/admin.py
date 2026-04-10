from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description_preview')
    search_fields = ('title',)

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    description_preview.short_description = 'Описание'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'video_link_preview')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

    def video_link_preview(self, obj):
        return obj.video_link[:50] + '...' if len(obj.video_link) > 50 else obj.video_link

    video_link_preview.short_description = 'Ссылка на видео'
