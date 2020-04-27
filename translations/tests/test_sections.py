import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from translations.models import Section, Category


class DownloadableListTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(
            name='1st Section',
            is_active=True
        )

        Category.objects.create(name='1st Category', section=section, is_active=True)
        Category.objects.create(name='2nd Category', section=section, is_active=True)
        super().setUpTestData()

    def test_section_list(self):
        url = reverse('section-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '1st Section')

    def test_has_categories(self):
        url = reverse('section-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(results[0]['categories'][0]['name'], '1st Category')
        self.assertEqual(results[0]['categories'][1]['name'], '2nd Category')
