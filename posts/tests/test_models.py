from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='UserTest')
        
        cls.group = Group.objects.create(
            title = 'задайте заголовок',
            slug = 'test_slug',
            description = 'Описание группы'
        )

        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = cls.user,
            group = cls.group,
        )

    def setUp(self):
        self.guest_client = Client()


    def test_verbose_name(self):
        """verbose_name post в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text group в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Задайте заголовок',
            'description': 'Описание группы. Не более 400 символов',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_post_fild(self):
        """__str__  text в post- это строчка с содержимым post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEquals(expected_object_name, str(post))

    def test_object_name_is_group_fild(self):
        """__str__  title в group - это строчка с содержимым group.title."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
            