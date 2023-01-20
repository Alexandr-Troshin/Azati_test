from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly

from rest_framework import fields, serializers

from .models import Orders, Transactions, OrdersDjangoLog
from .serializer import OrdersSerializer, TransactionsSerializer, \
    OrdersDjangoSerializer, TransactionsDjangoSerializer

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
    queryset = OrdersDjango.objects.all().order_by('-order_dttm')
    serializer_class = OrdersDjangoSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['user_name']


    def create(self, request, *args, **kwargs):
        """ Переопределение функции создания объекта. При создании нового заказа информация о нем
        дублируется в лог-таблицу, проверяется возможность совершения транзакций с существующими
        заказами, выполненные транзакции сохраняются в таблицу транзакций, данные текущего списка
        заказов обновляются с учетом прошедших транзакций"""
        with transaction.atomic():
            serializer = OrdersDjangoSerializer(data=request.data, context={'request': request})
#            print(request.data)
            serializer.is_valid(raise_exception=True)
#            print(serializer.validated_data)
            order_details = dict(serializer.validated_data)
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
