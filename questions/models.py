from __future__ import annotations

from typing import FrozenSet, Set

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django_access_control.models import all_field_names
from django_access_control.permissions import has_permission
from django_access_control.querysets import ConfidentialQuerySet


class QuestionQuerySet(ConfidentialQuerySet):
    def has_table_wide_add_permission(self, user: AbstractUser) -> bool:
        return user.is_authenticated

    def rows_with_view_permission(self, user: AbstractUser) -> QuerySet[Question]:
        return super().rows_with_view_permission(user) | self.filter(is_published=True) | \
               (self.filter(creator=user) if user.is_authenticated else self.none())

    def rows_with_change_permission(self, user: AbstractUser) -> QuerySet[Question]:
        if user.is_staff:
            return self
        return (self if super().has_table_wide_change_permission(user) else self.none()) | \
               (self.filter(creator=user) if user.is_authenticated else self.none())

    def changeable_fields(self, user: AbstractUser, obj: Question) -> FrozenSet[str]:
        if user.is_superuser or has_permission(user, "change", obj.__class__):
            return frozenset(all_field_names(obj.__class__))
        if obj.creator == user: return frozenset({"body"})
        if user.is_staff: return frozenset({"is_published"})
        return frozenset()


class Question(models.Model):
    title = models.CharField(max_length=30)
    body = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    is_published = models.BooleanField(default=True)

    objects = QuestionQuerySet.as_manager()
    default_confidential_manager = ConfidentialQuerySet.as_manager()

    def __str__(self) -> str:
        return self.title
