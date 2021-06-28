from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_access_control.models import all_field_names

from forum import settings
from questions.models import Question


class BaseQuestionsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        question_content_type = ContentType.objects.get_for_model(Question)
        add_permission = Permission.objects.get(codename='add_question', content_type=question_content_type)
        view_permission = Permission.objects.get(codename='view_question', content_type=question_content_type)
        change_permission = Permission.objects.get(codename='change_question', content_type=question_content_type)
        delete_permission = Permission.objects.get(codename='delete_question', content_type=question_content_type)

        cls.superuser = User.objects.create_superuser("superuser")

        cls.add_permission_holder = User.objects.create_user("adder")
        cls.add_permission_holder.user_permissions.add(add_permission)

        cls.view_permission_holder = User.objects.create_user("viewer")
        cls.view_permission_holder.user_permissions.add(view_permission)

        cls.change_permission_holder = User.objects.create_user("changer")
        cls.change_permission_holder.user_permissions.add(change_permission)

        cls.delete_permission_holder = User.objects.create_user("deleter")
        cls.delete_permission_holder.user_permissions.add(delete_permission)

        cls.staff_member = User.objects.create_user("staff", is_staff=True)
        cls.user_one = User.objects.create_user("user_one")
        cls.user_two = User.objects.create_user("user_two")

        cls.question = Question.objects.create(title="Ipsum?", body="Lorem ipsum.", creator=cls.user_one)

        cls.qs = Question.default_confidential_manager.get_queryset()


class ConfidentialQuerySetTest(BaseQuestionsTestCase):

    def test_superuser_has_full_access(self):
        # table wide permissions
        self.assertTrue(self.qs.has_table_wide_add_permission(self.superuser))
        self.assertTrue(self.qs.has_table_wide_view_permission(self.superuser))
        self.assertTrue(self.qs.has_table_wide_change_permission(self.superuser))
        self.assertTrue(self.qs.has_table_wide_delete_permission(self.superuser))

        # row permissions
        self.assertTrue(self.qs.rows_with_view_permission(self.superuser).contains(self.question))
        self.assertTrue(self.qs.rows_with_change_permission(self.superuser).contains(self.question))
        self.assertTrue(self.qs.rows_with_delete_permission(self.superuser).contains(self.question))

        # field permissions
        self.assertEqual(self.qs.viewable_fields(self.superuser, self.question), all_field_names(self.question))
        self.assertEqual(self.qs.changeable_fields(self.superuser, self.question), all_field_names(self.question))

        self.assertTrue(self.qs.has_some_permissions(self.superuser))

    def test_add_permission_holder_access(self):
        user = self.add_permission_holder

        # table wide permissions
        self.assertTrue(self.qs.has_table_wide_add_permission(user))
        self.assertFalse(self.qs.has_table_wide_view_permission(user))
        self.assertFalse(self.qs.has_table_wide_change_permission(user))
        self.assertFalse(self.qs.has_table_wide_delete_permission(user))

        # row permissions
        self.assertFalse(self.qs.rows_with_view_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_change_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_delete_permission(user).contains(self.question))

        self.assertTrue(self.qs.has_some_permissions(user))

    def test_view_permission_holder_access(self):
        user = self.view_permission_holder

        # table wide permissions
        self.assertFalse(self.qs.has_table_wide_add_permission(user))
        self.assertTrue(self.qs.has_table_wide_view_permission(user))
        self.assertFalse(self.qs.has_table_wide_change_permission(user))
        self.assertFalse(self.qs.has_table_wide_delete_permission(user))

        # row permissions
        self.assertTrue(self.qs.rows_with_view_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_change_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_delete_permission(user).contains(self.question))

        self.assertTrue(self.qs.has_some_permissions(user))

    def test_change_permission_holder_access(self):
        user = self.change_permission_holder

        # table wide permissions
        self.assertFalse(self.qs.has_table_wide_add_permission(user))
        self.assertFalse(self.qs.has_table_wide_view_permission(user))
        self.assertTrue(self.qs.has_table_wide_change_permission(user))
        self.assertFalse(self.qs.has_table_wide_delete_permission(user))

        # row permissions
        self.assertFalse(self.qs.rows_with_view_permission(user).contains(self.question))
        self.assertTrue(self.qs.rows_with_change_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_delete_permission(user).contains(self.question))

        self.assertTrue(self.qs.has_some_permissions(user))

    def test_delete_permission_holder_access(self):
        user = self.delete_permission_holder

        # table wide permissions
        self.assertFalse(self.qs.has_table_wide_add_permission(user))
        self.assertFalse(self.qs.has_table_wide_view_permission(user))
        self.assertFalse(self.qs.has_table_wide_change_permission(user))
        self.assertTrue(self.qs.has_table_wide_delete_permission(user))

        # row permissions
        self.assertFalse(self.qs.rows_with_view_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_change_permission(user).contains(self.question))
        self.assertTrue(self.qs.rows_with_delete_permission(user).contains(self.question))

        self.assertTrue(self.qs.has_some_permissions(user))

    def test_permissionless_user_access(self):
        user = self.user_one

        # table wide permissions
        self.assertFalse(self.qs.has_table_wide_add_permission(user))
        self.assertFalse(self.qs.has_table_wide_view_permission(user))
        self.assertFalse(self.qs.has_table_wide_change_permission(user))
        self.assertFalse(self.qs.has_table_wide_delete_permission(user))

        # row permissions
        self.assertFalse(self.qs.rows_with_view_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_change_permission(user).contains(self.question))
        self.assertFalse(self.qs.rows_with_delete_permission(user).contains(self.question))

        self.assertFalse(self.qs.has_some_permissions(user))
