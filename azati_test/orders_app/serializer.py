from rest_framework import fields, serializers
from .models import Orders, TransLastOrder, Transactions, OrdersDjango, TransactionsDjango


# сериализаторы для работы с бизнес-логикой в триггерах базы
class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Orders
        fields = ("id", "user_name", "stock", "shares", "price_per_share", "order_type", "order_dttm")


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Transactions
        fields = ("id", "stock", "shares", "price_per_share", "buyer_name", "seller_name", "trans_dttm")


class TransLastOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TransLastOrder
        fields = ("id", "user_name", "stock", "shares", "price_per_share",
                  "order_type", "sum_shares", "order_dttm")

# сериализаторы для работы с бизнес-логикой в Django
class OrdersDjangoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrdersDjango
        fields = ("id", "user_name", "stock", "shares", "price_per_share", "order_type", "order_dttm")


class TransactionsDjangoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TransactionsDjango
        fields = ("id", "stock", "shares", "price_per_share", "buyer_name", "seller_name", "trans_dttm")