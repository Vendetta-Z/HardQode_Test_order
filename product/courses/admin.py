from django.contrib import admin
from .models import Course, Lesson, Group


class CourseAdmin(admin.ModelAdmin):
    list_display = ('author', 'title','id')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('course', 'id')
    filter_horizontal = ('students',)  # Удобный вид для ManyToManyField


admin.site.register(Course, CourseAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Lesson)
