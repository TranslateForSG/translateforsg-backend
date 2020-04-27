import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from translations.models import Downloadable, Language, Category


class DownloadableListTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        bn = Language.objects.create(
            name='Bengali',
            native_name='Bengali',
            code='bn',
            is_active=True
        )
        zh = Language.objects.create(
            name='Chinese',
            native_name='Chinese',
            code='zh',
            is_active=True
        )
        cat = Category.objects.create(
            name='Hola',
            is_active=True
        )
        Downloadable.objects.create(
            name='Test Downloadable',
            downloadable_file=SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4"),
            description='This is a downloadable file',
            language=bn
        )
        Downloadable.objects.create(
            name='Test Downloadable ZH',
            downloadable_file=SimpleUploadedFile("file_zh.mp4", b"file_content zh", content_type="video/mp4"),
            description='This is a downloadable file ZH',
            language=zh,
            category=cat
        )
        super().setUpTestData()

    def test_downloadable_list(self):
        url = reverse('downloadable-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'Test Downloadable')
        self.assertEqual(results[0]['description'], 'This is a downloadable file')
        self.assertTrue('downloadables/file' in results[0]['downloadable_file'])

    def test_language_filter(self):
        url = reverse('downloadable-list')
        response = self.client.get(url + '?language__name=Chinese')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Test Downloadable ZH')
        self.assertEqual(results[0]['description'], 'This is a downloadable file ZH')
        self.assertTrue('downloadables/file_zh' in results[0]['downloadable_file'])

    def test_category_filter(self):
        url = reverse('downloadable-list')
        response = self.client.get(url + '?category__name=Hola')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Test Downloadable ZH')
        self.assertEqual(results[0]['description'], 'This is a downloadable file ZH')
        self.assertTrue('downloadables/file_zh' in results[0]['downloadable_file'])

    def test_category_filter_no_exist(self):
        url = reverse('downloadable-list')
        response = self.client.get(url + '?category__name=Ebola')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 0)
