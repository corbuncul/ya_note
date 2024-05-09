from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='User_1')
        cls.user_2 = User.objects.create(username='User_2')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='note_1', author=cls.user_1
        )

    def test_pages_availability(self):
        """
        Проверка доступности Главной страницы,
        страниц логина, логаута и регистрации для всех клиентов.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_delete_detail(self):
        """
        Проверка доступности автору заметок страниц просмотра заметки,
        редактирования и удаления заметки и недоступности этих страниц
        с кодом 404 другим пользователям.
        """
        users_statuses = (
            (self.user_1, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        pages_note = (
            'notes:edit',
            'notes:delete',
            'notes:detail'
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in pages_note:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверка редиректа анонимных пользователей на страницу логина
        со страниц списка заметок, добавления заметки
        и страницы успешного завершения.
        """
        login_url = reverse('users:login')
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_list_create_and_done_for_authorized_client(self):
        """
        Проверка доступности авторизованному пользователю списка заметок,
        страницы создания заметки и страницы удачного завершения.
        """
        self.client.force_login(self.user_1)
        status = HTTPStatus.OK
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
