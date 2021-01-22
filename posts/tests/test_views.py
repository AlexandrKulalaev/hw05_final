import tempfile
import shutil
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.core.cache import cache
from django import forms

from posts.models import Post, Group, Follow, User


USERNAME = 'author'
SLUG = 'test_slug'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group', args=[SLUG])
PROFILE_URL = reverse('profile', args=[USERNAME])
IMAGE_URL = 'posts/small.gif'
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B'
                         )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

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
            image=cls.uploaded
        )

        cls.POST_EDIT_URL = reverse('post_edit', kwargs={
            'username': cls.user_author, 'post_id': cls.post.id})
        cls.POST_URL = reverse('post', kwargs={
            'username': cls.user_author, 'post_id': cls.post.id})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client_other = Client()
        self.authorized_client_author = Client()

        self.authorized_client_other.force_login(self.user_other)
        self.authorized_client_author.force_login(self.user_author)

    def test_post_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон. test_views"""
        template_pages_names = {
            'group.html': GROUP_URL,
            'index.html': INDEX_URL,
            'new.html': NEW_POST_URL,
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_other.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context_index(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(NEW_POST_URL)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(GROUP_URL)
        self.assertEqual(response.context.get('group').title,
                         'Группа для теста')
        self.assertEqual(response.context.get('group').description,
                         'Описание группы')
        self.assertEqual(response.context.get('group').slug, SLUG)
        self.assertEqual(response.context.get('page')[0].image, IMAGE_URL)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(INDEX_URL)
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_image_0, IMAGE_URL)

    def test_username_post_id_page_show_correct_context(self):
        """Шаблон <username> сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(PROFILE_URL)
        post_text_0 = response.context.get('page')[0].text
        self.assertEqual(post_text_0, PostPagesTest.post.text)
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_author_0, PostPagesTest.post.author)
        post_group_0 = response.context.get('page')[0].group
        self.assertEqual(post_group_0, PostPagesTest.post.group)
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_image_0, IMAGE_URL)

    def test_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            PostPagesTest.POST_EDIT_URL)
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_id_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(PostPagesTest.POST_URL)
        self.assertEqual(response.context.get('post').text, 'Текст')
        self.assertEqual(response.context.get('post').author, self.user_author)
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').image, IMAGE_URL)

    def test_cache(self):
        """Тестирование кэша"""
        response = self.authorized_client_author.get(INDEX_URL)
        response2 = self.authorized_client_author.get(INDEX_URL)
        self.assertHTMLEqual(str(response), str(response2))
        cache.clear()
        response3 = self.authorized_client_author.get(INDEX_URL)
        self.assertHTMLEqual(str(response), str(response3))


class PaginatorViewsTest(TestCase):

    POSTS_IN_PAGE = 10
    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_other = User.objects.create(username='other')

        Post.objects.bulk_create([Post(
            text=f'Тестовое сообщение{i}',
            author=cls.user_other)
            for i in range(cls.POSTS_COUNT)])

    def test_first_page_containse_ten_records(self):
        """Тест паджинатора."""
        response = self.client.get(INDEX_URL)
        self.assertEqual(len(response.context.get('page').object_list),
                         self.POSTS_IN_PAGE)

    def test_second_page_containse_three_records(self):
        response = self.client.get(INDEX_URL + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list),
                         self.POSTS_COUNT - self.POSTS_IN_PAGE)


class FollowUserViewTest(TestCase):

    FOLLOWER_USER = 'TestUser_01'
    NOT_FOLLOWER_USER = 'TestUser_02'

    def setUp(self):
        # создадим 2х пользователей.
        self.user_follower = get_user_model().objects.create(
            username=self.FOLLOWER_USER)
        self.user_not_follower = get_user_model().objects.create(
            username=self.NOT_FOLLOWER_USER)
        # Создадим 2 записи на нашем сайте
        Post.objects.create(text='Тест',
                            author=self.user_not_follower
                            )
        Post.objects.create(text='Тест',
                            author=self.user_follower
                            )
        # авторизуем подписчика
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        # авторизуем владельца записи на нашем сайте
        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.user_not_follower)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.user_not_follower
            }))
        self.assertTrue(Follow.objects.filter(user=self.user_follower,
                                              author=self.user_not_follower),
                        'Подписка на пользователя не рабоатет'
                        )

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        self.auth_client_follower.get(reverse(
            'profile_unfollow',
            kwargs={
                'username': self.user_not_follower
            }))
        self.assertFalse(Follow.objects.filter(user=self.user_follower,
                                               author=self.user_not_follower),
                         'Отписка от пользователя не работает'
                         )

    def test_post_added_to_follow(self):
        """Тестирование на правильность работы подписывания на пользователя"""
        # подпишем пользователя на auth_client_author
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.user_not_follower
            }))
        # получим все посты подписанного пользователя
        posts = Post.objects.filter(
            author__following__user=self.user_follower)
        response_follower = self.auth_client_follower.get(
            reverse('follow_index'))
        response_author = self.auth_client_author.get(
            reverse('follow_index'))
        # проверим содержание Context страницы follow_index пользователя
        # auth_client_follower и убедимся, что они имеются в ленте
        self.assertIn(posts.get(),
                      response_follower.context['paginator'].object_list,
                      'Запись отсутствует на странице подписок пользователя'
                      )
        # проверим содержание Context страницы follow_index пользователя
        # auth_client_author и убедимся, что записи в ленте не имеется
        self.assertNotIn(posts.get(),
                         response_author.context['paginator'].object_list,
                         'Запись добавлена к неверному пользователю.'
                         )
