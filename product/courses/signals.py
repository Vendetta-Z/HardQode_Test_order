from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription

from .models import Group, Course

@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """

    if created:
        pass
        # TODO


@receiver(post_save, sender=Course)
def create_groups_for_course(sender, instance, created, **kwargs):
    """Создаем 10 групп после создания нового курса."""
    if created:
        groups_to_create = 10
        for i in range(groups_to_create):
            Group.objects.create(course=instance)