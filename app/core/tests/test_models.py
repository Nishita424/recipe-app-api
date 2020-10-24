from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successful"""
        email = 'test@gmail.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_is_new_user_email_normalised(self):
        """Test the email for new user is normalised(lower case)"""
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(email=email,
                                                    password="test123")
        self.assertEqual(user.email, email.lower())

    def test_if_user_email_is_empty(self):
        """Test the new user email, and create user if email is not empty
        otherwise raise ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None,
                                                 password='test123')

    def test_create_new_super_user(self):
        """Test for new super user"""
        user = get_user_model().objects.create_superuser(
            email='test@GMAIL.com', password='password123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
