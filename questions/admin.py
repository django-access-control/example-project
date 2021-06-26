from django.contrib import admin
from django_access_control.admin import ConfidentialModelAdmin

from questions.models import Question


@admin.register(Question)
class QuestionAdmin(ConfidentialModelAdmin):
    pass
