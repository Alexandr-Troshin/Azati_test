from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Orders, Transactions, OrdersDjangoLog
from .serializer import OrdersSerializer, TransactionsSerializer

from .models import OrdersDjango, TransactionsDjango
from .serializer import OrdersDjangoSerializer, TransactionsDjangoSerializer


# вью-сеты для варианта с триггером
class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all().order_by('-order_dttm')
    serializer_class = OrdersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_name']


class TransactionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transactions.objects.all()
    serializer_class = TransactionsSerializer

# вью-сеты для бизнес-логики в Django
class OrdersDjangoViewSet(viewsets.ModelViewSet):

    queryset = OrdersDjango.objects.all().order_by('-order_dttm')
    serializer_class = OrdersDjangoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_name']

    def create(self, request, *args, **kwargs):
        order_details = request.POST.dict()
        order_details['shares'] = int(order_details['shares'])
        order_details['price_per_share'] = float(order_details['price_per_share'])
        del order_details['csrfmiddlewaretoken']
        counter_orders_list = self.get_counter_orders_list(order_details).values()
        created_obj = OrdersDjango.objects.create(**order_details)
        OrdersDjangoLog.objects.create(**order_details, order_action='PUT',
                                       order_id = created_obj.__dict__['id'])
        if counter_orders_list:
            for counter_order in counter_orders_list:
                print(counter_order)
                transaction_details = {'stock': order_details['stock'],
                                      'shares': min(order_details['shares'],
                                                    counter_order.get('shares')),
                                      'price_per_share': (order_details['price_per_share']
                                                          + counter_order.get('price_per_share'))/2}
                if order_details['order_type'] == 'SELL':
                    transaction_details['seller_name'] = order_details['user_name']
                    transaction_details['buyer_name'] = counter_order['user_name']
                else:
                    transaction_details['buyer_name'] = order_details['user_name']
                    transaction_details['seller_name'] = counter_order['user_name']
                TransactionsDjango.objects.create(**transaction_details)
                if order_details['shares'] >= counter_order['shares']:
                    order_details['shares'] -= counter_order['shares']
                    OrdersDjango.objects.filter(pk=counter_order['id']).delete()
                else:
                    OrdersDjango.objects.filter(pk=counter_order['id']).\
                        update(shares=(counter_order['shares'] - order_details['shares']))
                    order_details['shares'] = 0
                if order_details['shares'] == 0:
                    OrdersDjango.objects.filter(pk=created_obj.__dict__['id'])\
                                        .update(shares = 0)
                    OrdersDjango.objects.filter(pk=created_obj.__dict__['id']).delete()
                    break
            if order_details['shares'] > 0:
                OrdersDjango.objects.filter(pk=created_obj.__dict__['id'])\
                                    .update(shares = order_details['shares'])

        return self.get(request)

    def get_counter_orders_list(self, order_details:dict) -> queryset:
        """Функция возвращает queryset встречных заказов,
        с которыми можно провести транзакцию"""
        filtered_queryset = OrdersDjango.objects\
                                .exclude(user_name=order_details['user_name'])\
                                .exclude(order_type=order_details['order_type']) \
                                .filter(stock=order_details['stock'])
        if order_details['order_type'] == 'SELL':
            filtered_meet_price_requirements_queryset = filtered_queryset\
                .filter(price_per_share__gte = order_details['price_per_share'])
            sorting_order = '-price_per_share'
        else:
            filtered_meet_price_requirements_queryset = filtered_queryset \
                .filter(price_per_share__lte=order_details['price_per_share'])
            sorting_order = 'price_per_share'
        return filtered_meet_price_requirements_queryset.order_by(sorting_order, 'order_dttm')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        order_details = instance.__dict__
        OrdersDjangoLog.objects.create(order_id = order_details['id'],
                                       user_name = order_details['user_name'],
                                       stock = order_details['user_name'],
                                       shares = order_details['shares'],
                                       price_per_share = order_details['price_per_share'],
                                       order_type = order_details['order_type'],
                                       order_dttm = order_details['order_dttm'],
                                       order_action = 'DELETE')
        OrdersDjango.objects.filter(pk=order_details['id']).delete()
        return self.get(request)

class TransactionsDjangoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransactionsDjango.objects.all()
    serializer_class = TransactionsDjangoSerializer



# class OrdersList(generics.ListCreateAPIView):
#     queryset = Orders.objects.all().order_by('-order_dttm')
#     serializer_class = OrdersSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user_name']
#
#
# class OrdersDetail(generics.RetrieveAPIView):
#     queryset = Orders.objects.all()
#     serializer_class = OrdersSerializer

# class TransactionsList(generics.ListAPIView):
#     queryset = Transactions.objects.all()
#     serializer_class = TransactionsSerializer
#
#
# class TransactionsDetail(generics.RetrieveAPIView):
#     queryset = Transactions.objects.all()
#     serializer_class = TransactionsSerializer





