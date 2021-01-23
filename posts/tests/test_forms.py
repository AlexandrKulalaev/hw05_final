import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User
from . import constants as c


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )

        cls.user_author = User.objects.create(username='author')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=c.SLUG,
            description='Описание группы'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group,
            image=cls.uploaded
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user_other = get_user_model().objects.create(username='other')
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user_other)

    def test_create_post(self):
        """Валидная форма создает запись в Group."""
        post_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded.name,
        }

        response = self.authorized_client_other.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, c.INDEX_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Group.objects.filter(slug=c.SLUG).exists())


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text='Test post', author=cls.user)

    def test_edit_post(self):
        """При редактировании поста изменяется запись в Post."""
        form_data = {'text': 'Test post edited'}
        self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': 'test_user',
                    'post_id': PostFormTests.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.first().text, form_data['text'])
