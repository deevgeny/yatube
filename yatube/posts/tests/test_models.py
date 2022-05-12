from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста'
        )

    def test_model_have_correct_object_name(self):
        """Test model's __str__() method."""
        self.assertEqual(
            PostModelTest.post.text[:settings.TEXT_FIELD_LIMIT],
            str(PostModelTest.post),
            f'Неверно работает функция __str__() в модели {Post}'
        )

    def test_verbose_name(self):
        """Test model fields verbose_name attribute."""
        # Prepare test data
        error_msg = 'Неверное значение verbose_name поля {}'
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        # Run test
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value,
                    error_msg.format(field)
                )

    def test_help_text(self):
        """Test model fields help_text attribute."""
        # Prepare test data
        error_msg = 'Неверное значение help_text поля {}'
        field_help_texts = {
            'text': 'Введите текст поста',
            'pub_date': '',
            'author': '',
            'group': 'Группа, к которой будет относиться пост'
        }
        # Run test
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value,
                    error_msg.format(field)
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_model_have_correct_object_name(self):
        """Test model's __str__() method."""
        self.assertEqual(
            GroupModelTest.group.title,
            str(GroupModelTest.group),
            f'Неверно работает функция __str__() в модели {Group}'
        )

    def test_verbose_name(self):
        """Test model fields verbose_name attribute."""
        error_msg = 'Неверное значение verbose_name поля {}'
        field_verboses = {
            'title': 'title',
            'slug': 'slug',
            'description': 'description'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(field).verbose_name,
                    expected_value,
                    error_msg.format(field)
                )

    def test_help_text(self):
        """Test model fields help_text attribute."""
        error_msg = 'Неверное значение help_text поля {}'
        field_help_texts = {
            'title': '',
            'slug': '',
            'description': ''
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(field).help_text,
                    expected_value,
                    error_msg.format(field)
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='Comment_text'
        )

    def test_model_have_correct_object_name(self):
        """Test model's __str__() method."""
        self.assertEqual(
            CommentModelTest.comment.text[:settings.TEXT_FIELD_LIMIT],
            str(CommentModelTest.comment),
            f'Неверно работает функция __str__() в модели {Comment}'
        )

    def test_verbose_name(self):
        """Test model fields verbose_name attribute."""
        error_msg = 'Неверное значение verbose_name поля {}'
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(
                        field).verbose_name,
                    expected_value,
                    error_msg.format(field)
                )

    def test_help_text(self):
        """Test model fields help_text attribute."""
        error_msg = 'Неверное значение help_text поля {}'
        field_help_texts = {
            'post': '',
            'author': '',
            'text': 'Введите текст комментария',
            'created': ''
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(field).help_text,
                    expected_value,
                    error_msg.format(field)
                )
