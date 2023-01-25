from django.contrib.auth import authenticate, get_user_model
# from django.contrib.auth.models import User
import json
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(json.loads(user.balance_of_funds), {'money': 0})

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(username='')
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password="testpassword")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(username='testsuperuser',
                                                   password='testsuperpassword')
        self.assertEqual(admin_user.username, 'testsuperuser')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertFalse(admin_user.balance_of_funds)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='testsuperuser', password='testsuperpassword', is_superuser=False)


class SigninTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='12test12', email='test@example.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test', password='12test12')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='wrong', password='12test12')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_password(self):
        user = authenticate(username='test', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)