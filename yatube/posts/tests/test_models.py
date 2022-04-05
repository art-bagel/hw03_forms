from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем в базе данных тестового пользователя, пост и группу."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='qwert' * 30,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = str(PostModelTest.post)
        group = str(PostModelTest.group)
        self.assertEqual(post, 'qwertqwertqwert')
        self.assertEqual(group, 'Тестовая группа')
