from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import TagSerializer
from ..models import Tag

TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test-user@gmail.com', password='testpassword')
        self.client.force_authenticate(self.user)

    # get_tags
    def test_retrieve_tags(self):
        """Test that all tags are retrieved for logged in user"""
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True) # Otherwise list of tags
        # is treated as a single object

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for only requested authenticated
        user."""
        user2 = get_user_model().objects.create_user(
            email='test-user-2@gmail.com', password='testpassword2')
        Tag.objects.create(user=user2, name='Salad')

        tag = Tag.objects.create(user=self.user, name='Mandi')
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    # create_tag
    def test_create_tag_successful(self):
        """Test creating a new tag in db"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user, name=payload[
            'name']).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid_name(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
