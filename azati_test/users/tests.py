from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
# from django.contrib.auth.models import User
from django.urls import reverse
import json
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient, force_authenticate

User = get_user_model()

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
        #User = get_user_model()
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


    def test_user_register(self):
        url = reverse('register')
        user_data = { "username": "user1",
                      "email": "user@example.com",
                      "password": "user1password",
                      "password2": "user1password"
                    }
        user_data_response = {  "username": "user1",
                                "email": "user@example.com",
                                "balance_of_funds": {
                                    "money": 0
                                }
                              }
        response = self.client.post(url, user_data, format='json')
        #User.objects.delete(username='user1', password='user1password')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, user_data_response)


    def test_user_get_token(self):
        url = reverse('register')
        n_user = User.objects.count() + 1
        user_data = { "username": "user"+ str(n_user),
                      "email": "user@example.com",
                      "password": "user" + str(n_user) + "password",
                      "password2": "user" + str(n_user) + "password"
                    }
        self.client.post(url, user_data, format='json')
        url_token = reverse('token_obtain')
        user_token_data = {"username": "user"+ str(n_user),
                           "password": "user" + str(n_user) + "password"
                          }
        response = self.client.post(url_token, user_token_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])


    def test_user_update_funds_with_existing_stock(self):
        url = reverse('register')
        n_user = User.objects.count() + 1
        user_data = { "username": "user"+ str(n_user),
                      "email": "user@example.com",
                      "password": "user" + str(n_user) + "password",
                      "password2": "user" + str(n_user) + "password"}
        req_user = self.client.post(url, user_data, format='json')
        user_pk = User.objects.get(username=user_data['username']).pk
        url_token = reverse('token_obtain')
        user_token_data = {"username": "user"+ str(n_user),
                           "password": "user" + str(n_user) + "password"}
        response_token = self.client.post(url_token, user_token_data, format='json')
        url_update_funds = reverse('user_update_funds', kwargs={'pk': user_pk})
        update_data_correct = {"income_stock": "money",
                               "income_qty": 15000}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response_token.data["access"]}')
        response_update = self.client.post(url_update_funds, update_data_correct, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response_update.data, {"message": "money increased on 15000"})


    def test_user_update_funds_with_non_existing_stock_and_control_final_state(self):
        url = reverse('register')
        n_user = User.objects.count() + 1
        user_data = { "username": "user"+ str(n_user),
                      "email": "user@example.com",
                      "password": "user" + str(n_user) + "password",
                      "password2": "user" + str(n_user) + "password"}
        req_user = self.client.post(url, user_data, format='json')
        user_pk = User.objects.get(username=user_data['username']).pk
        url_token = reverse('token_obtain')
        user_token_data = {"username": "user"+ str(n_user),
                           "password": "user" + str(n_user) + "password"}

        response_token = self.client.post(url_token, user_token_data, format='json')
        url_update_funds = reverse('user_update_funds', kwargs={'pk': user_pk})
        update_data_correct = {"income_stock": "Tesla",
                               "income_qty": 15}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response_token.data["access"]}')
        response_update = self.client.post(url_update_funds, update_data_correct, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response_update.data, {"message": "Tesla increased on 15"})
        url_user_detail = reverse('user_detail', kwargs={'pk': user_pk})
        response_state = self.client.get(url_user_detail)
        self.assertEqual(response_state.status_code, status.HTTP_200_OK)
        self.assertEqual(response_state.data,{'username': 'user2',
                                              'email': 'user@example.com',
                                              'balance_of_funds': {'Tesla': 15, 'money': 0}})