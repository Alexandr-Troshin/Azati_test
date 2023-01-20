from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User

from .models import OrdersDjango, OrdersDjangoLog, TransactionsDjango


DATA_LIST = [
    {'stock': 'Tesla', 'order_type': 'SELL', 'shares': 150, 'price_per_share': 176},
    {'stock': 'Tesla', 'order_type': 'SELL', 'shares': 45, 'price_per_share': 175},
    {'stock': 'Tesla', 'order_type': 'BUY', 'shares': 120, 'price_per_share': 173},
    {'stock': 'Tesla', 'order_type': 'BUY', 'shares': 50, 'price_per_share': 173},
    {'stock': 'Tesla', 'order_type': 'BUY', 'shares': 35, 'price_per_share': 171.5},
    {'stock': 'Tesla', 'order_type': 'SELL', 'shares': 150, 'price_per_share': 173},
    {'stock': 'Tesla', 'order_type': 'BUY', 'shares': 100, 'price_per_share': 175},
]



class OrdersDjangoTests(APITestCase):
    """Проверка переопределенных функций"""

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='firstuser', email='test@example.com')
        cls.user1.save()
        cls.user2 = User.objects.create_user(username='user2', password='seconduser', email='test@example.com')
        cls.user2.save()
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

    def setUp(self):

#        user1 = authenticate(username='user1', password='firstuser')
        self.client.login(username='user1', password='firstuser')
        self.order1 = OrdersDjango.objects.create(**DATA_LIST[0])
        self.order1.save()
        self.client.logout()


    def test_create_order(self):
        """Проверка создания заказа"""
        #user = authenticate(username='user1', password='firstuser')
        self.client.login(username='user2', password='seconduser')
        url = reverse('orders_django_basename-list')
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.post(url, DATA_LIST[1], format='json')
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrdersDjango.objects.count() - objects_quantity_before_test, 1)
        self.assertEqual(OrdersDjango.objects.filter(pk=objects_quantity_before_test+1)
                         .get().user_id, 2)


    def test_delete_existing_order(self):
        """Проверка удаления существующего заказа."""
        self.client.login(username='user2', password='seconduser')
        url_add = reverse('orders_django_basename-list')
        self.client.post(url_add, DATA_LIST[1], format='json')
        last_pk = OrdersDjango.objects.last().pk
        url = reverse('orders_django_basename-detail', kwargs={'pk': last_pk})
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.delete(url, format='json', follow=True)
        self.client.logout()
#        print(OrdersDjango.objects.count())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(objects_quantity_before_test - OrdersDjango.objects.count(), 1)

    def test_delete_non_existing_order(self):
        """Проверка удаления НЕсуществующего заказа."""
        self.client.login(username='user2', password='seconduser')
        last_pk = OrdersDjango.objects.last().pk
        url = reverse('orders_django_basename-detail', kwargs={'pk': last_pk+1})
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.delete(url, format='json', follow=True)
        self.client.logout()
        #        print(OrdersDjango.objects.count())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(objects_quantity_before_test - OrdersDjango.objects.count(), 0)


class ScriptTests(APITestCase):
    """Проверка прохождения сценария"""

    @classmethod
    def setUpTestData(cls):
        for user_num in range(3, 10):
            cls.user = User.objects.create_user(username='user' + str(user_num),
                                                password='user' + str(user_num) + 'pass',
                                                email='test@example.com')
            cls.user.save()
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

    def setUp(self):
        url_add = reverse('orders_django_basename-list')
        for i in range(3, 8):
            self.client.login(username='user' + str(i), password='user' + str(i) + 'pass')
            self.client.post(url_add, DATA_LIST[i-3], format='json')
            self.client.logout()

    def test_script(self):
        """Проверка работоспособности сценария"""
        # стартовые условия - 5 заказов
        self.assertEqual(OrdersDjango.objects.count(), 5)
        self.assertEqual(OrdersDjangoLog.objects.count(), 5)
        self.assertEqual(TransactionsDjango.objects.count(), 0)
        # удаление первого заказа
        self.client.login(username='user3', password='user3pass')
        url_del = reverse('orders_django_basename-detail',
                          kwargs={'pk': OrdersDjango.objects.first().pk})
        response = self.client.delete(url_del, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OrdersDjango.objects.count(), 4)
        self.assertEqual(OrdersDjangoLog.objects.count(), 6)
        self.assertEqual(OrdersDjangoLog.objects.last().order_action, "DELETE")
        # добавление заказа [5] должно пройти 2 транзакции

        url_add = reverse('orders_django_basename-list')
        self.client.post(url_add, DATA_LIST[5], format='json')
        self.assertEqual(OrdersDjango.objects.count(), 3)
        self.assertEqual(OrdersDjangoLog.objects.count(), 7)
        self.assertEqual(TransactionsDjango.objects.count(), 2)
        first_object = TransactionsDjango.objects.first()
        self.assertEqual(first_object.shares, 120)
        self.assertEqual(first_object.price_per_share, 173)
        self.assertEqual(first_object.buyer_name, 'user5')
        self.assertEqual(first_object.seller_name, 'user3')
        last_object = TransactionsDjango.objects.last()
        self.assertEqual(last_object.shares, 30)
        self.assertEqual(last_object.price_per_share, 173)
        self.assertEqual(last_object.buyer_name, 'user6')
        self.assertEqual(last_object.seller_name, 'user3')
        self.assertEqual(OrdersDjango.objects.get(user_id=6).shares, 20)
        self.client.logout()
        # добавление заказа [6] должна добавиться 1 транзакция
        self.client.login(username='user8', password='user8pass')
        url_add = reverse('orders_django_basename-list')
        self.client.post(url_add, DATA_LIST[6], format='json')
        last_object = TransactionsDjango.objects.last()
        self.assertEqual(last_object.shares, 45)
        self.assertEqual(last_object.price_per_share, 175)
        self.assertEqual(last_object.buyer_name, 'user8')
        self.assertEqual(last_object.seller_name, 'user4')
        self.assertEqual(OrdersDjango.objects.count(), 3)
        self.assertEqual(OrdersDjangoLog.objects.count(), 8)
        test_object = OrdersDjango.objects.get(user_id=8)
        self.assertEqual(test_object.shares, 55)
        self.assertEqual(test_object.order_type, "BUY")
        self.client.logout()
