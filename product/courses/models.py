from django.db import models
from django.forms import ValidationError

from users.models import CustomUser

class Course(models.Model):
    """Модель продукта - курса."""

    author = models.CharField(
        max_length=250,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )

    price = models.PositiveBigIntegerField(
        default=1000,
        verbose_name='Цена'
    )



    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Уроки',
        related_name='lessons'

    )

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )

    # TODO

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
    )

    students = models.ManyToManyField(
        CustomUser,
        verbose_name='Студенты',
        blank=True
    )

    MAX_GROUPS_PER_COURSE = 10  # Лимит на количество групп
    MAX_STUDENTS_PER_GROUP = 30  # Лимит на количество студентов в группе

    def clean(self):
        """Проверка ограничений перед сохранением."""
        # Проверка, сколько групп уже существует для данного курса, если это новая группа
        if not self.pk:  # Проверяем, существует ли группа (id == None для новой группы)
            existing_groups_count = Group.objects.filter(course=self.course).count()

            # Если превышено количество групп
            if existing_groups_count >= self.MAX_GROUPS_PER_COURSE:
                raise ValidationError(f"Нельзя добавить больше {self.MAX_GROUPS_PER_COURSE} групп на курс.")
        
        if self.pk:  # Проверка только для уже существующей группы
            if self.students.count() > self.MAX_STUDENTS_PER_GROUP:
                raise ValidationError(f"В группе не может быть больше {self.MAX_STUDENTS_PER_GROUP} студентов.")
            
            
    def save(self, *args, **kwargs):
        """Проверка перед сохранением."""
        # проверяем количество сущ. групп
        self.clean()
        # После валидации сохраняем объект снова, если необходимо
        super().save(*args, **kwargs)
        

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('id',)
