from django.contrib import admin
from .models import CustomUser, Balance, Subscription

admin.site.register(CustomUser)
admin.site.register(Subscription)

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'id']

    def has_change_permission(self, request, obj=None):
        # Разрешаем изменение только для суперпользователей
        if not request.user.is_staff:
            return False
        return super().has_change_permission(request, obj)