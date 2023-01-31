import json

from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerOrReadOnly

from .models import Orders, Transactions, OrdersDjangoLog
from .serializer import OrdersSerializer, TransactionsSerializer, \
    OrdersDjangoSerializer, TransactionsDjangoSerializer
import pika

from .orders_services import *


# вью-сеты для варианта с триггером
class OrdersViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Orders.objects.all().order_by('-order_dttm')
    serializer_class = OrdersSerializer


class TransactionsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Transactions.objects.all()
    serializer_class = TransactionsSerializer


# вью-сеты для бизнес-логики в Django
class OrdersDjangoViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsOwnerOrReadOnly, )
    #queryset = OrdersDjango.objects.all().order_by('-order_dttm')
    def get_queryset(self):
         return OrdersDjango.objects.filter(user=self.request.user)

    serializer_class = OrdersDjangoSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['user_name']


    def create(self, request, *args, **kwargs):
        """ Переопределение функции создания объекта. При создании нового заказа информация о нем
        дублируется в лог-таблицу, проверяется возможность совершения транзакций с существующими
        заказами, выполненные транзакции сохраняются в таблицу транзакций, данные текущего списка
        заказов обновляются с учетом прошедших транзакций"""
        with transaction.atomic():
            current_user = User.objects.filter(username=request.user).first()
            serializer = OrdersDjangoSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order_details = dict(serializer.validated_data)
            if not is_funds_enough_for_order(current_user, order_details):
                return Response({'message': 'User have NOT enough funds to make this order'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                counter_orders_list = get_counter_orders_list(order_details).values()
                created_order = OrdersDjango.objects.create(**order_details)
                created_order_id = created_order.__dict__['id']
                OrdersDjangoLog.objects.create(**order_details, order_action='PUT',
                                               order_id=created_order_id)
                if counter_orders_list:
                    make_trasactions_and_update_orders_list(order_details, counter_orders_list,
                                                            created_order_id)
        return Response(OrdersDjangoSerializer(created_order).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """ Переопределение функции удаления объекта. Перед удалением объекта создает запись
         в лог-таблице с характеристиками заказа и пометкой DELETE"""
        with transaction.atomic():
            instance = self.get_object()
            order_id = instance.pk
            order_details = instance.__dict__
#            print('order_details', order_details)
            OrdersDjangoLog.objects.create(order_id=order_details['id'],
                                           user=User.objects.get(pk=order_details['user_id']),
                                           stock=order_details['stock'],
                                           shares=order_details['shares'],
                                           price_per_share=order_details['price_per_share'],
                                           order_type=order_details['order_type'],
                                           order_dttm=order_details['order_dttm'],
                                           order_action='DELETE')
            instance.delete()
        return Response({'message': f'Order {order_id} deleted'}, status=status.HTTP_204_NO_CONTENT)


class TransactionsDjangoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = TransactionsDjango.objects.all()
    serializer_class = TransactionsDjangoSerializer


class RabbitMQView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, *args, **kwargs):
        credentials = pika.PlainCredentials('rabbit', 'rabbit_password')
        conn_params = pika.ConnectionParameters('rabbitmq3', # '127.0.0.1',
                                                5672,
                                                '/',
                                                credentials)

        def start_consumer():
            connection = pika.BlockingConnection(conn_params)
            channel = connection.channel()
            channel.queue_declare(queue='orders', durable=True)

            # method = 'put_order'

            def callback(ch, method, properties, body):
                if properties.content_type == 'put_order':
                    print(" [x] Received:", body)
                    order_dict = json.loads(body.decode())
                    create_from_queue(order_dict)
                    print(" [x] Received:", body.decode())
                elif properties.content_type == 'stop_consuming':
                    channel.stop_consuming('0')
                    quit()

            channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=True)

            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

        start_consumer()
