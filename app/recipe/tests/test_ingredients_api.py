"""Test Ingredients API"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Ingredient Specific URL"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return new user"""
    return get_user_model().objects.create_user(email=email,password=password)


class PublicIngredientApiTests(TestCase):
    """Test Unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test Authentication required"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test Authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving all the ingredients"""
        Ingredient.objects.create(user=self.user, name='Sample Ingredient 1')
        Ingredient.objects.create(user=self.user, name='Sample Ingredient 2')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients limited to authenticated user"""
        unauthenticated_user = create_user(email='abc@gmail.com')
        Ingredient.objects.create(user=unauthenticated_user, name='Tea Masala')
        ingredient = Ingredient.objects.create(user=self.user, name='Cardamom')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        url = detail_url(ingredient.id)
        payload = {'name': 'Ginger'}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_ingredient(self):
        """Test deleting ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Water')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())


