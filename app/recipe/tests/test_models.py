from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Tag


def sample_user(email='test@admin.com', password='password'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_tag_str(self):
        """Test the tag model string representation"""
        tag = Tag.objects.create(
            user=sample_user(), name='Vegan')
        self.assertEqual(str(tag), tag.name)
