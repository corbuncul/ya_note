from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another = User.objects.create(username='Другой')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.url_create = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_done = reverse('notes:success')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_client = Client()
        cls.another_client.force_login(cls.another)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anoninous_user_cant_create_note(self):
        """Проверка, что аноним не может создать заметку."""
        response = self.client.post(self.url_create, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(notes_count, 1)

    def test_anonimous_user_cant_delete_note(self):
        """Проверка, что аноним не может удалить заметку"""
        response = self.client.delete(self.url_delete)
        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(notes_count, 1)

    def test_author_can_create_note(self):
        """Проверка, что авторизованный пользователь может создать заметку."""
        response = self.author_client.post(
            self.url_create,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_author_can_edit_note(self):
        """
        Проверка, что авторизованный пользователь
        может редактировать свои заметки.
        """
        response = self.author_client.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_done)
        note = Note.objects.get()
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        """
        Проверка, что авторизованный пользователь
        может удалять свои заметки.
        """
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_another_user_cant_edit_note_of_author(self):
        """
        Проверка, что другой пользователь не может
        редактировать заметки автора.
        """
        response = self.another_client.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.slug, self.note.slug)

    def test_another_user_cant_delete_note_of_author(self):
        """
        Проверка, что другой пользователь не может
        удалить заметку автора.
        """
        response = self.another_client.delete(self.url_delete)
        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, 1)
