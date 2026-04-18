from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'description_preview', 'lessons_count')
    list_filter = ('owner',)
    search_fields = ('title', 'description')
    readonly_fields = ('owner',)

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    description_preview.short_description = 'Описание'

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Количество уроков'

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'preview', 'description')
        }),
        ('Владелец', {
            'fields': ('owner',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner', 'video_link_preview')
    list_filter = ('course', 'owner')
    search_fields = ('title', 'description', 'course__title')
    readonly_fields = ('owner',)

    def video_link_preview(self, obj):
        return obj.video_link[:50] + '...' if len(obj.video_link) > 50 else obj.video_link

    video_link_preview.short_description = 'Ссылка на видео'

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'preview', 'video_link')
        }),
        ('Курс', {
            'fields': ('course',)
        }),
        ('Владелец', {
            'fields': ('owner',)
        }),
    )
