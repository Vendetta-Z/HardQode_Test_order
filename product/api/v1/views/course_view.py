from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions 
from rest_framework.exceptions import PermissionDenied

from api.v1.permissions import ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from courses.models import Course, Group, Lesson
from users.models import Balance, IsCoursePurchased, Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = [IsCoursePurchased]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        """Возвращаем только уроки для курсов, которые пользователь купил."""
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(id=course_id)

        # Проверяем, купил ли пользователь курс
        if not Subscription.objects.filter(Subscriber=self.request.user, course=course).exists():
            raise PermissionDenied("Вы не приобрели этот курс.")
        
        return Lesson.objects.filter(course=course)


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = Course.objects.get(id=self.kwargs.get('course_id'))
        course_groups = Group.objects.filter(course=course)
        return course_groups
    

class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = [ReadOnlyOrIsAdmin, IsCoursePurchased]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        course = Course.objects.get(id=pk)
        user_balance = Balance.objects.get(user = request.user)
        if user_balance.amount < course.price:
            raise ValidationError("Недостаточно средств на счету.")
        
        # Списываем деньги с кошелька
        user_balance.amount -= course.price
        user_balance.save()
        
        # Создаем запись о покупке
        Subscription.objects.create(Subscriber=request.user, course=course)

         # Найти свободную группу
        group = self.find_available_group(course)
        if group:
            group.students.add(request.user)
            group.save()
            message = " Курс успешно приобретён и вы добавлены в группу."
        else:
            message = " Курсc успешно приобретён, но нет доступных групп для записи."

        return Response(
            {'Оплата успешно прошла!'},
            status=status.HTTP_201_CREATED
        )


    def find_available_group(self, course):
        """Находит первую свободную группу для данного курса."""
        groups = Group.objects.filter(course=course)
        for group in groups:
            if group.students.count() < Group.MAX_STUDENTS_PER_GROUP:
                return group
        return None