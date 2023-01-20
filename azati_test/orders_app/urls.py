from django.contrib.auth.views import LoginView
from django.urls import path, include, re_path
from djoser.views import UserViewSet
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import OrdersViewSet, TransactionsViewSet
from .views import OrdersDjangoViewSet, TransactionsDjangoViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    # path('api/v1/register/', UserViewSet.as_view({'post': 'create'}), name="register"),
    # path("api/v1/login/", TokenObtainPairView.as_view(), name="login"),
    # path("api/v1/resend-activation/", UserViewSet.as_view({"post": "resend_activation"}), name="resend_activation"),
    # path("api/v1/activation/<str:uid>/<str:token>/", UserViewSet.as_view({"post": "activate"}), name="activate"),
    # path("api/v1/reset-password/", UserViewSet.as_view({"post": "reset_password"}), name="reset_password"),
    # path("api/v1/reset-password-confirm/<str:uid>/<str:token>/", UserViewSet.as_view({"post": "reset_password_confirm"}), name="reset_password_confirm"),
    # path('api/v1/auth/', include('djoser.urls')),
    # path('api/v1/auth/', include('djoser.urls.jwt')),

#   re_path(r'^auth/', include('djoser.urls.jwt')),
#    path('api/v1/api-auth/', include('rest_framework.urls')),
#     path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/v1/orders/', views.OrdersList.as_view()),
    # path('api/v1/orders/<int:pk>/', views.OrdersDetail.as_view()),
    # path('api/v1/transactions/', views.TransactionsList.as_view()),
    # path('api/v1/transactions/<int:pk>/', views.TransactionsDetail.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
