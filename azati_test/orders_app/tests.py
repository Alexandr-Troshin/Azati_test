from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.test import APIRequestFactory

from .models import OrdersDjango, OrdersDjangoLog, TransactionsDjango


DATA_LIST = [
    {'user_name': 'Adam', 'stock': 'Tesla', 'order_type': 'SELL', 'shares': 150, 'price_per_share': 176},
    {'user_name': 'Bob', 'stock': 'Tesla', 'order_type': 'SELL', 'shares': 45, 'price_per_share': 175},
    {'user_name': 'Alice', 'stock': 'Tesla', 'order_type': 'BUY', 'shares': 120, 'price_per_share': 173},
    {'user_name': 'John', 'stock': 'Tesla', 'order_type': 'BUY', 'shares': 50, 'price_per_share': 173},
    {'user_name': 'Mike', 'stock': 'Tesla', 'order_type': 'BUY', 'shares': 35, 'price_per_share': 171.5},
    {'user_name': 'Adam', 'stock': 'Tesla', 'order_type': 'SELL', 'shares': 150, 'price_per_share': 173},
    {'user_name': 'Julia', 'stock': 'Tesla', 'order_type': 'BUY', 'shares': 100, 'price_per_share': 175},
]


class OrdersDjangoTests(APITestCase):
    """Проверка переопределенных функций"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.order1 = OrdersDjango.objects.create(**DATA_LIST[0])
        self.order1.save()

    def test_create_order(self):
        """Проверка создания заказа"""
        url = reverse('orders_django_basename-list')
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.post(url, DATA_LIST[1], format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrdersDjango.objects.count() - objects_quantity_before_test, 1)
        self.assertEqual(OrdersDjango.objects.filter(pk=objects_quantity_before_test+1)
                         .get().user_name, 'Bob')

    def test_delete_existing_order(self):
        """Проверка удаления заказа существующего заказа."""
        url_add = reverse('orders_django_basename-list')
        self.client.post(url_add, DATA_LIST[1], format='json')
        last_pk = OrdersDjango.objects.last().pk
        url = reverse('orders_django_basename-detail', kwargs={'pk': last_pk})
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.delete(url, format='json', follow=True)
#        print(OrdersDjango.objects.count())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(objects_quantity_before_test - OrdersDjango.objects.count(), 1)

    def test_delete_non_existing_order(self):
        """Проверка удаления заказа существующего заказа."""

        last_pk = OrdersDjango.objects.last().pk
        url = reverse('orders_django_basename-detail', kwargs={'pk': last_pk+1})
        objects_quantity_before_test = OrdersDjango.objects.count()
        response = self.client.delete(url, format='json', follow=True)
        #        print(OrdersDjango.objects.count())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(objects_quantity_before_test - OrdersDjango.objects.count(), 0)


class ScriptTests(APITestCase):
    """Проверка переопределенных функций"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        url_add = reverse('orders_django_basename-list')
        for i in range(5):
            self.client.post(url_add, DATA_LIST[i], format='json')

    def test_script(self):
        """Проверка работоспособности сценария"""
        # стартовые условия - 5 заказов
        self.assertEqual(OrdersDjango.objects.count(), 5)
        self.assertEqual(OrdersDjangoLog.objects.count(), 5)
        self.assertEqual(TransactionsDjango.objects.count(), 0)
        # удаление первого заказа
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
        self.assertEqual(TransactionsDjango.objects.first().shares, 120)
        self.assertEqual(TransactionsDjango.objects.first().price_per_share, 173)
        self.assertEqual(TransactionsDjango.objects.first().buyer_name, 'Alice')
        self.assertEqual(TransactionsDjango.objects.first().seller_name, 'Adam')
        self.assertEqual(TransactionsDjango.objects.last().shares, 30)
        self.assertEqual(TransactionsDjango.objects.last().price_per_share, 173)
        self.assertEqual(TransactionsDjango.objects.last().buyer_name, 'John')
        self.assertEqual(TransactionsDjango.objects.last().seller_name, 'Adam')
        self.assertEqual(OrdersDjango.objects.get(user_name="John").shares, 20)
        # добавление заказа [6] должна добавиться 1 транзакция
        url_add = reverse('orders_django_basename-list')
        self.client.post(url_add, DATA_LIST[6], format='json')
        self.assertEqual(TransactionsDjango.objects.last().shares, 45)
        self.assertEqual(TransactionsDjango.objects.last().price_per_share, 175)
        self.assertEqual(TransactionsDjango.objects.last().buyer_name, 'Julia')
        self.assertEqual(TransactionsDjango.objects.last().seller_name, 'Bob')
        self.assertEqual(OrdersDjango.objects.count(), 3)
        self.assertEqual(OrdersDjangoLog.objects.count(), 8)
        self.assertEqual(OrdersDjango.objects.get(user_name="Julia").shares, 55)
        self.assertEqual(OrdersDjango.objects.get(user_name="Julia").order_type, "BUY")
