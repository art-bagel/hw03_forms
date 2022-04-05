from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем пользователя."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        """Создаем анонимного и авторизованного клиента."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        # self.token = default_token_generator.make_token(self.user)

    def test_url_exists_at_desired_location(self):
        """Страницы из url_names_httpstatus доступны всем пользователям."""
        url_names_httpstatus = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for url, httpstatus in url_names_httpstatus.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, httpstatus)

    def test_url_available_authorized_user(self):
        """Страницы изменения параля доступны авторизованному
        пользователю.
        """
        url_names_httpstatus = {
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK
        }
        self._sub_test('Equal', url_names_httpstatus, self.authorized_client)

    def test_url_redirect_anonymous_on_login(self):
        """Страницы изменения пароля перенаправят
        незарегистрированного пользователя на страницу авторизации.
        """
        url_names_redirect = {
            reverse('users:password_change'):
                reverse('users:login')
                + '?next=' + reverse('users:password_change'),
            reverse('users:password_change_done'):
                reverse('users:login')
                + '?next=' + reverse('users:password_change_done')
        }
        self._sub_test('Redirects', url_names_redirect, self.guest_client)

    # def test_url_password_reset_confirm(self):
    #     """URL-подтверждения параля, на которую переходит пользователь из своей
    #      почты.
    #      """
    #     url = reverse('users:password_reset_confirm',
    #                   kwargs={'uidb64': self.uid, 'token': self.token})
    #     self.response = self.authorized_client.get(url, follow=True)
    #     self.assertEqual(url, HTTPStatus.OK)

    def test_uses_correct_templates(self):
        """"URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html',
            # reverse('users:password_reset_confirm',
            #         kwargs={'uidb64': self.uid, 'token': self.token}):
            #     'users/password_reset_confirm.html'
        }
        self._sub_test('TemplateUsed', url_names_templates, self.authorized_client)

    def _sub_test(self, assert_method: str,
                  dictionary,
                  client: Client
                  ) -> None:
        """Универсальный subTest метод."""
        for address, result in dictionary.items():
            with self.subTest(address=address):
                response = client.get(address, follow=True)
                if assert_method == 'Equal':
                    self.assertEqual(response.status_code, result)
                elif assert_method == 'Redirects':
                    self.assertRedirects(response, result)
                elif assert_method =='TemplateUsed':
                    self.assertTemplateUsed(response, result)
