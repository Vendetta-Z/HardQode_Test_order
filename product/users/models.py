from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.permissions import BasePermission


class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)
        
    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE, 
        default=None,
        verbose_name='Пользователь'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name='Количество бонусов'
    )

    def __str__(self):
        return f'{self.user.username} - Balance: {self.amount}'

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Курс подписки'
    )
    Subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Пользователь подписки'
    )

    def get_subscriptions(self):
        return Subscription.objects.filter(Subscriber=self.user)
    

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)


class IsCoursePurchased(BasePermission):
    """Проверка, купил ли пользователь курс для доступа к урокам."""
    
    def has_object_permission(self, request, view, obj):
        """Проверяем, купил ли пользователь курс для данного урока."""
        course = obj.course
        return Subscription.objects.filter(Subscriber=request.user, course=course).exists()