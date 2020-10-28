from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Creates user into db"""
    # params: dynamic list of args, for more flexibility
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    # create_user
    def test_create_valid_user_success(self):
        """Test creating user with valid payload(input) is successful"""
        payload = {
            'email': 'nish@user.com',
            'password': 'testpass',
            'name': 'Test user'
        }
        response = self.client.post(CREATE_USER_URL, payload) # json object
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password'])) # User
        # object created should have same data as in payload
        self.assertNotIn('password', response.data) # User password should
        # not be returned in the user object, so we are checking that
        # password is not in response data

    def test_user_exists(self):
        """Test for creating a user that already exists fail"""
        payload = {
            'email': 'nish@user.com',
            'password': 'testpass',
            'name': 'Test user'
        }
        create_user(**payload) # Creating user already
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            'email': 'nish@user.com',
            'password': 'pw',
            'name': 'Test user'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_given_email_already_exists(self):
        """Test that email is already used"""
        payload = {
            'email': 'nish@user.com',
            'password': 'password123',
            'name': 'Test user'
        }
        does_user_exist = get_user_model().objects.filter(email=payload[
            'email']).exists()
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertFalse(does_user_exist)

    # create_token
    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {
            'email': 'test@user.com',
            'password': 'testpass'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data) # Check for 'token'(k,v) is
        # returned in response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created, when invalid credentials are
        given"""
        create_user(email='test@gmail.com', password='testpass')
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrongpass'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user do not exist"""
        payload = {
            'email': 'test@user.com',
            'password': 'testpass'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        response = self.client.post(TOKEN_URL, {'email': 'test@gmail.com',
                                                'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # manage user profile endpoint - check that authenticated user can edit
    # his profile
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for user to edit his profile"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserApiTests(TestCase):
        """Test api requests that require authentication"""
        def setUp(self):
            self.user = create_user(email='test@gmail.com', password='pswd',
                                    name='Test-user')
            self.client = APIClient()
            self.client.force_authenticate(user=self.user)

        def test_retrieve_profile_success(self):
            """Test for retrieving profile with logged in user"""
            response = self.client.get(ME_URL)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {
                'name': self.user.name,
                'email': self.user.email
            })

        def test_post_operation_not_allowed(self):
            """Test that post operation is not allowed on any url"""
            response = self.client.post(ME_URL, {})
            self.assertEqual(response.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_profile_successful(self):
            """Test updating the user profile for authenticated user"""
            payload = {
                'password': 'new-pswd',
                'name': 'new-Test-user'
            } # details diff from ones given in setUp()
            response = self.client.put(ME_URL, payload) # put vs patch:
            # put is used to update the entire object, patch is used to
            # update only specific fields of the object
            self.user.refresh_from_db()
            self.assertEqual(self.user.name, payload['name'])
            self.assertTrue(self.user.check_password(payload['password']))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # How to test update user profile?
        # 1. Download "mod header" chrome extension
        # 2. Add a row: key="Authorization" value=tokenid (You can update as
        # long as token id you give here do not expire, if expired call
        # api/user/create/token/ again)
        # 3. Call api/user/me/, you can update email, name, password here
        # Update all at once if you use 'put', to update only specific fields
        # use 'patch'
        # 4. After updating check user login with updated credentials
