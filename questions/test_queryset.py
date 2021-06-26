from django.contrib.auth.models import User
from django.test import TestCase
from django_access_control.models import all_field_names

from forum import settings
from questions.models import Question


class QuestionQuerySetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = User.objects.create_superuser("superuser")
        cls.change_permission_holder = User.objects.create_user("changer")
        cls.delete_permission_holder = User.objects.create_user("deleter")
        cls.staff_member = User.objects.create_user("staff", is_staff=True)
        cls.user_one = User.objects.create_user("user_one")
        cls.user_two = User.objects.create_user("user_two")

        cls.question = Question.objects.create(title="Ipsum?", body="Lorem ipsum.", creator=cls.user_one)

    def test_superuser_has_full_access(self):
        qs = Question.objects.get_queryset()
        self.assertTrue(qs.has_table_wide_add_permission(self.superuser))
        self.assertTrue(qs.has_table_wide_view_permission(self.superuser))
        self.assertTrue(qs.has_table_wide_change_permission(self.superuser))
        self.assertTrue(qs.has_table_wide_delete_permission(self.superuser))

        self.assertTrue(qs.rows_with_view_permission(self.superuser).contains(self.question))
        self.assertTrue(qs.rows_with_change_permission(self.superuser).contains(self.question))
        self.assertTrue(qs.rows_with_delete_permission(self.superuser).contains(self.question))

        self.assertEqual(qs.viewable_fields(self.superuser, self.question), all_field_names(self.question))
        self.assertEqual(qs.changeable_fields(self.superuser, self.question), all_field_names(self.question))

        self.assertTrue(qs.has_some_permissions(self.superuser))
