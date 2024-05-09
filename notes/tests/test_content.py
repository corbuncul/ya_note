from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    NUMBER_OF_NOTES = 25
    LIST_NOTES_URL = reverse('notes:list')
    MAX_SLUG_LENGTH = 100
    NOTE_TITLE = 'Заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        for index in range(cls.NUMBER_OF_NOTES):
            note = Note(
                title=f'{cls.NOTE_TITLE} {index}',
                text='Просто текст.',
                author=cls.author
            )
            note.save()

    def test_notes_count(self):
        """Проверка количества выводимых заметок"""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_NOTES_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.NUMBER_OF_NOTES)

    def test_notes_slug_unique(self):
        """Проверка уникальности slug"""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_NOTES_URL)
        object_list = response.context['object_list']
        all_slug = [note.slug for note in object_list]
        all_slug_set = set(all_slug)
        self.assertEqual(len(all_slug), len(all_slug_set))

    def test_authorized_client_has_form(self):
        """Проверка формы на странице редактирования заметки."""
        self.client.force_login(self.author)
        slug = slugify(f'{self.NOTE_TITLE} 1')[:self.MAX_SLUG_LENGTH]
        note_url = reverse('notes:edit', args=(slug,))
        response = self.client.get(note_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
