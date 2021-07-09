from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client

from questions.models import Question


class BaseAdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_member = User.objects.create_user(username="staff", password="xxx", is_staff=True)
        cls.user_1 = User.objects.create_user(username="user_1", password="xxx")
        cls.user_2 = User.objects.create_user(username="user_2", password="xxx")

        cls.staff_member_client = Client()
        cls.staff_member_client.login(username="staff", password="xxx")
        cls.user_1_client = Client()
        cls.user_1_client.login(username="user_1", password="xxx")
        cls.user_2_client = Client()
        cls.user_2_client.login(username="user_2", password="xxx")
        cls.anonymous_client = Client()

        cls.question_1 = Question.objects.create(title="Lorem", body="Foo bar", author=cls.user_1)
        cls.question_2 = Question.objects.create(title="Imsum", body="Foo bar", author=cls.user_2, is_published=False)


class ListViewTest(BaseAdminTestCase):

    @staticmethod
    def get_list_page_table(client: Client):
        response = client.get("/questions/question/")
        return str(BeautifulSoup(response.content, 'html.parser').select("#result_list > tbody")[0])

    def test_staff_member_sees_all_questions(self):
        table = self.get_list_page_table(self.staff_member_client)
        self.assertTrue("Lorem" in table)
        self.assertTrue("Imsum" in table)

    def test_anonymous_user_sees_only_published_questions(self):
        table = self.get_list_page_table(self.anonymous_client)
        self.assertTrue("Lorem" in table)
        self.assertTrue("Imsum" not in table)

    def test_user_1_sees_only_published_questions(self):
        table = self.get_list_page_table(self.user_1_client)
        self.assertTrue("Lorem" in table)
        self.assertTrue("Imsum" not in table)

    def test_user_2_sees_only_published_questions_and_their_own_questions(self):
        table = self.get_list_page_table(self.user_2_client)
        self.assertTrue("Lorem" in table)  # This one is published
        self.assertTrue("Imsum" in table)  # This one is not published, but user_2 sees it because they are the author


class AddViewTest(BaseAdminTestCase):
    ADD_VIEW_URL = "/questions/question/add"

    @classmethod
    def get_add_page_form(cls, client: Client):
        response = client.get(cls.ADD_VIEW_URL, follow=True)
        return str(BeautifulSoup(response.content, 'html.parser').find(id="question_form"))

    def test_staff_member_can_submit_three_fields(self):
        table = self.get_add_page_form(self.staff_member_client)
        self.assertTrue('<div class="form-row field-title">' in table)
        self.assertTrue('<div class="form-row field-body">' in table)
        self.assertTrue('<div class="form-row field-is_published">' in table)

    def test_anonymous_user_cannot_add_question(self):
        response = self.anonymous_client.get(self.ADD_VIEW_URL, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_can_submit_two_fields(self):
        table = self.get_add_page_form(self.user_1_client)
        self.assertTrue('<div class="form-row field-title">' in table)
        self.assertTrue('<div class="form-row field-body">' in table)
        self.assertTrue('<div class="form-row field-is_published">' not in table)


class ChangeViewTest(BaseAdminTestCase):
    CHANGE_VIEW_URL = "/questions/question/{}/change/"

    @classmethod
    def get_change_page_form(cls, client: Client, question_pk: int):
        response = client.get(cls.CHANGE_VIEW_URL.format(question_pk), follow=True)
        return str(BeautifulSoup(response.content, 'html.parser').find(id="question_form"))

    def test_anonymous_user_view(self):
        """
        Anonymous users and logged in users without special privileges can view but not change the question.

        As seen in the assert statements, all fields are displayed readonly, not as input cells.
        """
        table = self.get_change_page_form(self.anonymous_client, self.question_1.pk)
        self.assertInHTML('<label>Title:</label><div class="readonly">Lorem</div>', table)
        self.assertInHTML('<label>Body:</label><div class="readonly">Foo bar</div>', table)
        self.assertInHTML(
            '<label>Author:</label><div class="readonly"><a href="/auth/user/2/change/">user_1</a></div>', table)

    def test_author_view(self):
        """
        The author of the question can update the `body` and see `title`, `author` and `is_published` as readonly fields
        """
        table = self.get_change_page_form(self.user_1_client, self.question_1.pk)
        self.assertInHTML('<label>Title:</label><div class="readonly">Lorem</div>', table)
        # The label's `for` attribute is present only on editable fields
        self.assertInHTML('<label class="required" for="id_body">Body:</label>', table)
        self.assertInHTML(
            '<label>Author:</label><div class="readonly"><a href="/auth/user/2/change/">user_1</a></div>', table)
        self.assertInHTML(
            '<div><label>Is published:</label><div class="readonly"><img src="/static/admin/img/icon-yes.svg" '
            'alt="True"></div></div>', table)

    def test_staff_view(self):
        """
        The staff member can update the `body` and `is_published` fields and see `title` and `author` as readonly fields
        """
        table = self.get_change_page_form(self.staff_member_client, self.question_1.pk)
        self.assertInHTML('<label>Title:</label><div class="readonly">Lorem</div>', table)
        # The label's `for` attribute is present only on editable fields
        self.assertInHTML('<label>Body:</label><div class="readonly">Foo bar</div>', table)
        self.assertInHTML(
            '<label>Author:</label><div class="readonly"><a href="/auth/user/2/change/">user_1</a></div>', table)
        self.assertInHTML(
            '<input type="checkbox" name="is_published" id="id_is_published" checked="">'
            '<label class="vCheckboxLabel" for="id_is_published">Is published</label>', table)
