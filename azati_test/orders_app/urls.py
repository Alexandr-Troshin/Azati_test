from django.urls import path, include
from rest_framework import routers
from .views import OrdersViewSet, TransactionsViewSet, RabbitMQView
from .views import OrdersDjangoViewSet, TransactionsDjangoViewSet


router_orders = routers.SimpleRouter()
router_orders.register(r'orders', OrdersViewSet)

router_transactions = routers.SimpleRouter()
router_transactions.register(r'transactions', TransactionsViewSet)

router_orders_django = routers.SimpleRouter()
router_orders_django.register(r'orders_django', OrdersDjangoViewSet, basename='orders_django_basename')

router_transactions_django = routers.SimpleRouter()
router_transactions_django.register(r'transactions_django', TransactionsDjangoViewSet)


urlpatterns = [
    path('', include(router_orders.urls)),
    path('', include(router_transactions.urls)),
    path('', include(router_orders_django.urls)),
    path('', include(router_transactions_django.urls)),
    path('rabbitmq/', RabbitMQView.as_view())
]
