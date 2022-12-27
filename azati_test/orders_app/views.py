from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Orders, TransLastOrder, Transactions
from .serializer import OrdersSerializer, TransLastOrderSerializer, TransactionsSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all().order_by('-order_dttm')
    serializer_class = OrdersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_name']


class TransactionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transactions.objects.all()
    serializer_class = TransactionsSerializer



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





