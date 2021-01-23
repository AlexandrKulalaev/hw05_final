from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User
from . import constants as c


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create(username='author')
        cls.user_other = User.objects.create(username='other')

        cls.group = Group.objects.create(
            title='Группа для теста',
            slug=c.SLUG,
            description='Описание группы'
        )

        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client_other = Client()
        self.authorized_client_author = Client()

        self.authorized_client_other.force_login(PostURLTests.user_other)
        self.authorized_client_author.force_login(PostURLTests.user_author)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(c.INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_username_url_exists_at_desired_location(self):
        """Страница /author/ доступна любому пользователю."""
        response = self.guest_client.get(c.PROFILE_URL)
        self.assertEqual(response.status_code, 200)

    def test_username_post_url_exists_at_desired_location(self):
        """Страница /author/post доступна любому пользователю."""
        response = self.guest_client.get(
            f'/{PostURLTests.user_author}/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client_other.get(c.NEW_POST_URL)
        self.assertEqual(response.status_code, 200)

    def test_slug_url_exists_at_desired_location_authorized(self):
        """Страница /group/test-slug/ доступна авторизованному
        пользователю."""
        response = self.authorized_client_other.get(c.GROUP_URL)
        self.assertEqual(response.status_code, 200)

    def test_edit_url_redirect_anonymous_on_admin_login(self):
        """Незарегестрированного пользователя при попытке редактирование поста
        редиректит на логирование"""
        response = self.guest_client.get(
            f'/{PostURLTests.user_author}/{PostURLTests.post.id}/edit/',
            follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{PostURLTests.user_author}/'
            f'{PostURLTests.post.id}/edit/')

    def test_edit_url_redirect_auth_users(self):
        """Залогированному пользователю не доступно редактирование поста,
                                                        если он не автор"""
        response = self.authorized_client_other.get(
            reverse("post_edit", args=[PostURLTests.user_author.username,
                                       PostURLTests.post.id]), follow=True)
        self.assertRedirects(
            response, f'/{PostURLTests.user_author}/{PostURLTests.post.id}/')

    def test_auth_author_user_page_edit(self):
        """Автору поста доступно редактирование поста"""
        response = self.authorized_client_author.get(
            reverse("post_edit", args=[PostURLTests.user_author.username,
                                       PostURLTests.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон test_urls."""
        templates_url_names = {
            'index.html': c.INDEX_URL,
            'new.html': c.NEW_POST_URL,
            'group.html': c.GROUP_URL,
            'misc/500.html': c.ERROR500_URL,
            'misc/404.html': c.ERROR400_URL,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_other.get(reverse_name)
                self.assertTemplateUsed(response, template)


class StaticURLTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_homepage(self):

        response = self.guest_client.get(c.INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_author(self):

        response = self.guest_client.get(c.ABOUT_AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_tech(self):

        response = self.guest_client.get(c.ABOUT_TECH_URL)
        self.assertEqual(response.status_code, 200)
