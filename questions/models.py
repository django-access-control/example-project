from __future__ import annotations

from typing import FrozenSet, Set

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django_access_control.models import all_field_names
from django_access_control.querysets import ConfidentialQuerySet


class QuestionQuerySet(ConfidentialQuerySet):
    def has_table_wide_add_permission(self, user: AbstractUser) -> bool:
        print("Add permission", user.is_authenticated)
        return user.is_authenticated

    def rows_with_extra_view_permission(self, user: AbstractUser) -> QuerySet[Question]:
        if user.is_staff:
            return self
        return self.filter(is_published=True) | (self.filter(author=user) if user.is_authenticated else self.none())

    def rows_with_extra_change_permission(self, user: AbstractUser) -> QuerySet[Question]:
        if user.is_staff:
            return self
        return self.filter(author=user) if user.is_authenticated else self.none()

    @classmethod
    def addable_fields(cls, user: AbstractUser) -> FrozenSet[str]:
        """
        Here we can already assume that the user has add permission.
        """
        if user.is_staff: return frozenset({"title", "body", "is_published"})
        return frozenset({"title", "body"})

    @staticmethod
    def changeable_fields(user: AbstractUser, obj: Question) -> FrozenSet[str]:
        if user.is_superuser: return frozenset(all_field_names(obj.__class__))
        fields = frozenset()
        if obj.author == user: fields |= frozenset({"body"})
        if user.is_staff: fields |= frozenset({"is_published"})
        return fields

    @staticmethod
    def viewable_fields(user: AbstractUser, obj) -> FrozenSet[str]:
        if user.is_superuser or user.is_staff or obj.author == user: return frozenset(all_field_names(obj.__class__))
        return frozenset({"title", "body", "author"})


class Question(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    is_published = models.BooleanField(default=True)

    objects = QuestionQuerySet.as_manager()
    default_confidential_manager = ConfidentialQuerySet.as_manager()

    def __str__(self) -> str:
        return self.title
