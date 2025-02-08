"""
Test for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='password123'):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Test the publicly available tags API."""

    def setUp(self):
        """Set up the test."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that login is required to access the tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test the authorized user tags API."""

    def setUp(self):
        """Set up the test."""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Get the tags from the API.
        res = self.client.get(TAGS_URL)

        # Get the tags from the db.
        # Tag is a class attribute of the Tag model.
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        # Check that the response is successful and the data is correct.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user."""
        user2 = create_user('user2@example.com', 'password123')
        Tag.objects.create(user=user2, name='Fruity')
        Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        # Check that the API returned the current user's tags only.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'Comfort Food')

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertEqual(tags.exists(), False)
