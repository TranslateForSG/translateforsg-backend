import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from translations.models import Category, UserType


class CategoryListTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        doctor = UserType.objects.create(name='Doctor', is_active=True)
        UserType.objects.create(name='Everyone', is_active=True)

        Category.objects.create(name='Inactive Category', is_active=False)
        active = Category.objects.create(name='Active Category', is_active=True)
        active.intended_for.add(doctor)

        super().setUpTestData()

    def test_category_list(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Active Category')

    def test_category_list_intended_for(self):
        url = reverse('category-list')
        response = self.client.get(url + '?intended_for__name=Doctor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Active Category')

    def test_category_list_intended_for_no_match(self):
        url = reverse('category-list')
        response = self.client.get(url + '?intended_for__name=Everyone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_content = json.loads(response.content)
        results = json_content['results']

        self.assertEqual(len(results), 0)
