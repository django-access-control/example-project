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

        cls.question_1 = Question.objects.create(title="Lorem", body="Foo bar", creator=cls.user_1)
        cls.question_2 = Question.objects.create(title="Imsum", body="Foo bar", creator=cls.user_2, is_published=False)


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
        table = self.get_list_page_table(self.user_1_client)
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
