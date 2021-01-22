from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


USERNAME = 'other'
SLUG = 'test_slug'
ABOUT_AUTHOR_URL = '/about/author/'
ABOUT_TECH_URL = '/about/tech/'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group', args=[SLUG])
PROFILE_URL = reverse('profile', args=[USERNAME])
ERROR500_URL = reverse('error500')
ERROR400_URL = reverse('error404')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create(username='author')
        cls.user_other = User.objects.create(username='other')

        cls.group = Group.objects.create(
            title='Группа для теста',
            slug=SLUG,
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
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_username_url_exists_at_desired_location(self):
        """Страница /author/ доступна любому пользователю."""
        response = self.guest_client.get(PROFILE_URL)
        self.assertEqual(response.status_code, 200)

    def test_username_post_url_exists_at_desired_location(self):
        """Страница /author/post доступна любому пользователю."""
        response = self.guest_client.get(
            f'/{PostURLTests.user_author}/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client_other.get(NEW_POST_URL)
        self.assertEqual(response.status_code, 200)

    def test_slug_url_exists_at_desired_location_authorized(self):
        """Страница /group/test-slug/ доступна авторизованному
        пользователю."""
        response = self.authorized_client_other.get(GROUP_URL)
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
            'index.html': INDEX_URL,
            'new.html': NEW_POST_URL,
            'group.html': GROUP_URL,
            'misc/500.html': ERROR500_URL,
            'misc/404.html': ERROR400_URL,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_other.get(reverse_name)
                self.assertTemplateUsed(response, template)


class StaticURLTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_homepage(self):

        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_author(self):

        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_tech(self):

        response = self.guest_client.get(ABOUT_TECH_URL)
        self.assertEqual(response.status_code, 200)
