from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from users.models import CustomUser

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""
    
    class Meta:
        model = Lesson  
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""
        less_count = Lesson.objects.filter(course = obj).count()
        return less_count


    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""
        groups_student_on_this_cuourse = Group.objects.filter(course=obj).annotate(num_students=Count('students'))
        student_for_all_course_group = 0
        for group in groups_student_on_this_cuourse:
            student_for_all_course_group += group.num_students
        return student_for_all_course_group

    def get_groups_filled_percent(self, obj):
        """Процент заполненности всех групп в курсе и средний процент."""
        
        groups = Group.objects.filter(course=obj) # Получаем все группы для данного курса
        total_filled_percent = 0
        total_groups = groups.count()
        group_filled_percents = []# Список для хранения процентов заполненности каждой группы
        max_students_per_group = Group.MAX_STUDENTS_PER_GROUP # Максимальное количество студентов в группе

        for group in groups:
            students_count = group.students.count() # Количество студентов в группе
            percent_filled = (students_count / max_students_per_group) * 100  # Процент заполненности группы
            group_filled_percents.append({
                'group_id': group.id,
                'percent_filled': round(percent_filled, 2)  # Округляем до двух знаков
            })
            
            total_filled_percent += percent_filled # Суммируем процент для среднего значения
        average_filled_percent = (total_filled_percent / total_groups) if total_groups > 0 else 0  # Средний процент заполненности всех групп

        return round(average_filled_percent, 2) 
            # group_filled_percents для процентов заполненности по группам
            # round(average_filled_percent, 2) для среднего процент заполненности
        

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        all_users_count = CustomUser.objects.all().count()
        course_students_count = self.get_students_count(obj)
        demand_course_percent = course_students_count / all_users_count  * 100
        return round(demand_course_percent)

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'start_date',
            'price',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""
    students = StudentSerializer(many=True, read_only=True)  # Вложенный сериализатор для студентов
    course = serializers.CharField(source='course.title')
    class Meta:
        model = Group
        fields = (
            'course',  # Название курса
            'students',  # Список студентов
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'course',
            'students',
        )