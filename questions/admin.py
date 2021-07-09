from django.contrib import admin
from django_access_control.admin import ConfidentialModelAdmin

from questions.models import Question


@admin.register(Question)
class QuestionAdmin(ConfidentialModelAdmin):

    def save_model(self, request, obj, form, change):
        if not change: obj.author = request.user  # `not change` means the obj is added, not modified
        super().save_model(request, obj, form, change)
