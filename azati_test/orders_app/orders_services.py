from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from .models import OrdersDjango, TransactionsDjango, OrdersDjangoLog
from rest_framework import status
from rest_framework.response import Response

from .serializer import OrdersDjangoSerializer

# from django.contrib.auth.models import User


User = get_user_model()

def get_counter_orders_list(order_details: dict) -> QuerySet:
    """Функция возвращает queryset встречных заказов,
    с которыми можно провести транзакцию"""
    filtered_queryset = OrdersDjango.objects \
        .exclude(user_id=order_details['user'].id) \
        .exclude(order_type=order_details['order_type']) \
        .filter(stock=order_details['stock'])
    if order_details['order_type'] == 'SELL':
        filtered_meet_price_requirements_queryset = filtered_queryset \
            .filter(price_per_share__gte=order_details['price_per_share'])
        sorting_order = '-price_per_share'
    else:
        filtered_meet_price_requirements_queryset = filtered_queryset \
            .filter(price_per_share__lte=order_details['price_per_share'])
        sorting_order = 'price_per_share'
    return filtered_meet_price_requirements_queryset.order_by(sorting_order, 'order_dttm')


def _change_balances_according_transaction(buyer, seller, transaction_details, order_details):
    """Функция вносит изменения в balance_of_funds покупателя и продавца
    в соответствии с условиями транзакции"""
    transaction_details['seller_name'] = seller
    seller.balance_of_funds[order_details['stock']] -= transaction_details['shares']
    seller.balance_of_funds['money'] += transaction_details['shares'] * \
                                        transaction_details['price_per_share']
    seller.save()

    transaction_details['buyer_name'] = buyer
    if order_details['stock'] in buyer.balance_of_funds:
        buyer.balance_of_funds[order_details['stock']] += transaction_details['shares']
    else:
        buyer.balance_of_funds[order_details['stock']] = transaction_details['shares']
    buyer.balance_of_funds['money'] += transaction_details['shares'] * \
                                       transaction_details['price_per_share']
    buyer.save()
    return transaction_details

def _make_transaction(order_details, counter_order) -> None:
    """Функция создания транзакции на основе поступающего и встречного заказов.
    Транзакция сохраняется в базе данных"""
    transaction_details = {'stock': order_details['stock'],
                           'shares': min(order_details['shares'],
                                         counter_order.get('shares')),
                           'price_per_share': (order_details['price_per_share']
                                               + counter_order.get('price_per_share')) / 2}
    print(transaction_details)
    if order_details['order_type'] == 'SELL':
        buyer = User.objects.get(pk=counter_order['user_id'])
        seller = User.objects.get(username=order_details['user'].username)

        transaction_details = _change_balances_according_transaction(buyer, seller,
                                                                     transaction_details,
                                                                     order_details)

    else:
        buyer = User.objects.get(username=order_details['user'].username)
        seller = User.objects.get(pk=counter_order['user_id'])
        transaction_details = _change_balances_according_transaction(buyer, seller,
                                                                     transaction_details,
                                                                     order_details)
    print(transaction_details)
    TransactionsDjango.objects.create(**transaction_details)


def make_trasactions_and_update_orders_list(order_details, counter_orders_list, created_order_id) -> None:
    """Функция создания транзакций для списка встреных заказов. Транзакции сохраняется в базе данных,
    данные об остатках закказов, не закрытых транзакциями, обновляются."""
    for counter_order in counter_orders_list:
        _make_transaction(order_details, counter_order)
        if order_details['shares'] >= counter_order['shares']:
            order_details['shares'] -= counter_order['shares']
            OrdersDjango.objects.filter(pk=counter_order['id']).delete()
        else:
            OrdersDjango.objects.filter(pk=counter_order['id']). \
                update(shares=(counter_order['shares'] - order_details['shares']))
            order_details['shares'] = 0
        if order_details['shares'] == 0:
            OrdersDjango.objects.filter(pk=created_order_id) \
                .update(shares=0)
            OrdersDjango.objects.filter(pk=created_order_id).delete()
            break
    if order_details['shares'] > 0:
        OrdersDjango.objects.filter(pk=created_order_id) \
            .update(shares=order_details['shares'])

def is_funds_enough_for_order(current_user, order_details):
    if order_details.get('order_type') == 'SELL':
        if  ((order_details.get('stock') in current_user.balance_of_funds) and
             (order_details.get('shares') <=
                            current_user.balance_of_funds.get(order_details.get('stock')))):
            return True
        else:
            return False
    else:
        if (order_details.get('shares')*order_details.get('price_per_share') <=
                    current_user.balance_of_funds.get('money')):
            return True
        else:
            return False


def create_from_queue(order_dict, *args, **kwargs):
    """Функция получения orders из очереди RabbitMQ. При создании нового заказа информация о нем
    дублируется в лог-таблицу, проверяется возможность совершения транзакций с существующими
    заказами, выполненные транзакции сохраняются в таблицу транзакций, данные текущего списка
    заказов обновляются с учетом прошедших транзакций"""
    with transaction.atomic():
        current_user = User.objects.filter(username=order_dict['user']).first()
        order_details = order_dict
        print(order_details)
        order_details['user'] = current_user
        if not is_funds_enough_for_order(current_user, order_details):
            print('Not enough funds')
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
            print(OrdersDjangoSerializer(created_order).data)
    return Response(OrdersDjangoSerializer(created_order).data, status=status.HTTP_201_CREATED)
