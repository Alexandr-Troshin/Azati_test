from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import OrdersViewSet, TransactionsViewSet

router_orders = routers.SimpleRouter()
router_orders.register(r'orders', OrdersViewSet)

router_transactions = routers.SimpleRouter()
router_transactions.register(r'transactions', TransactionsViewSet)

urlpatterns = [
    path('api/v1/', include(router_orders.urls)),
    path('api/v1/', include(router_transactions.urls)),
    # path('api/v1/orders/', views.OrdersList.as_view()),
    # path('api/v1/orders/<int:pk>/', views.OrdersDetail.as_view()),
    # path('api/v1/transactions/', views.TransactionsList.as_view()),
    # path('api/v1/transactions/<int:pk>/', views.TransactionsDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
