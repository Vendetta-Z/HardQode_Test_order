# Generated by Django 4.2.10 on 2024-08-18 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_lesson_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.course', verbose_name='Курс группы'),
            preserve_default=False,
        ),
    ]
