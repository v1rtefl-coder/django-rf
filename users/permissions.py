from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    """
    Проверка, является ли пользователь модератором
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()

class IsOwner(permissions.BasePermission):
    """
    Проверка, является ли пользователь владельцем объекта
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
