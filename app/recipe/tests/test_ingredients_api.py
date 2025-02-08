"""
Tests for ingredient APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email="user@example.com", password="password123"):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsAPITests(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self):
        """Set up the test."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that login is required to access the ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test the authorized user ingredients API."""

    def setUp(self):
        """Set up the test."""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients."""
        Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Pepper")

        # Get the ingredients from the API.
        res = self.client.get(INGREDIENTS_URL)

        # Get the ingredients from the db.
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned."""
        user2 = create_user(email="user2@example.com")
        Ingredient.objects.create(user=user2, name="Vinegar")
        Ingredient.objects.create(user=self.user, name="Tumeric")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Tumeric")

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")

        payload = {"name": "Basil"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredent(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name="Cabbage")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
